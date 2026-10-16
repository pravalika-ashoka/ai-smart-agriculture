import asyncio
import json
import urllib.error
import urllib.parse
import urllib.request

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


# ============================================================
# PATHS AND CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
CACHE_FILE = BASE_DIR / "data" / "market_cache.json"

PRIMARY_API_URL = "https://mandi-api.onrender.com/v1/prices"

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
DATA_SOURCE = "Data.gov.in"
PRIMARY_SOURCE = "Mandi API"

MAX_ARRIVAL_AGE_DAYS = 14


# ============================================================
# CUSTOM EXCEPTION
# ============================================================

class MarketAPIError(Exception):
    pass


# ============================================================
# CACHE LOADER
# ============================================================

def load_market_cache() -> dict:
    if not CACHE_FILE.exists():
        raise MarketAPIError(
            "Government market price cache is not available."
        )

    try:
        with CACHE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, OSError) as error:
        raise MarketAPIError(
            "Unable to read the government market price cache."
        ) from error

    if not isinstance(data, dict):
        raise MarketAPIError("Invalid market cache.")

    if not isinstance(data.get("records", []), list):
        raise MarketAPIError("Invalid market cache records.")

    return data


# ============================================================
# HELPERS
# ============================================================

def matches_filter(value, filter_value: Optional[str]) -> bool:
    if not filter_value or not filter_value.strip():
        return True

    if value is None:
        return False

    return (
        str(value).strip().casefold()
        == filter_value.strip().casefold()
    )


def parse_arrival_date(value):
    if not value:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(
                str(value).strip(), fmt
            ).date()
        except ValueError:
            continue

    return None


def normalize_market_record(record: dict) -> Optional[dict]:
    """
    Normalize alternative API records and reject invalid data.
    """

    if not isinstance(record, dict):
        return None

    arrival = parse_arrival_date(record.get("arrival_date"))

    if arrival is None:
        return None

    today = datetime.now(timezone.utc).date()

    # Reject future records and records older than 14 days.
    if arrival > today or arrival < today - timedelta(
        days=MAX_ARRIVAL_AGE_DAYS
    ):
        return None

    try:
        minimum = float(record["min_price"])
        maximum = float(record["max_price"])
        modal = float(record["modal_price"])
    except (KeyError, TypeError, ValueError):
        return None

    # Reject negative prices and inconsistent price ranges.
    if (
        minimum < 0
        or maximum < minimum
        or modal < minimum
        or modal > maximum
    ):
        return None

    state = record.get("state")
    district = record.get("district")
    market = record.get("market")
    commodity = record.get("commodity")

    if not all([state, district, market, commodity]):
        return None

    return {
        "state": state,
        "district": district,
        "market": market,
        "commodity": commodity,
        "variety": record.get("variety"),
        "grade": record.get("grade"),
        "arrival_date": arrival.isoformat(),
        "min_price": minimum,
        "max_price": maximum,
        "modal_price": modal,
    }


# ============================================================
# FETCH PRIMARY API
# ============================================================

def _fetch_primary_api(
    state: Optional[str],
    commodity: Optional[str],
) -> list:
    """
    Fetch market records from the alternative Mandi API.
    """

    params = {}

    if state and state.strip():
        params["state"] = state.strip()

    if commodity and commodity.strip():
        params["commodity"] = commodity.strip()

    url = PRIMARY_API_URL

    if params:
        url += "?" + urllib.parse.urlencode(params)

    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=25,
        ) as response:
            if response.status != 200:
                raise MarketAPIError(
                    f"Primary API returned HTTP {response.status}."
                )

            payload = json.loads(
                response.read().decode("utf-8")
            )

    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ) as error:
        raise MarketAPIError(
            "Unable to retrieve primary market data."
        ) from error

    if not isinstance(payload, dict):
        raise MarketAPIError("Invalid primary API response.")

    if payload.get("success") is not True:
        raise MarketAPIError("Primary API reported failure.")

    records = payload.get("data")

    if not isinstance(records, list):
        raise MarketAPIError("Primary API returned invalid records.")

    normalized = []

    for record in records:
        clean_record = normalize_market_record(record)

        if clean_record is not None:
            normalized.append(clean_record)

    if not normalized:
        raise MarketAPIError(
            "Primary API returned no valid recent market records."
        )

    # Most recent arrival dates first.
    normalized.sort(
        key=lambda record: record["arrival_date"],
        reverse=True,
    )

    return normalized


# ============================================================
# FILTER RECORDS
# ============================================================

def filter_records(
    records: list,
    commodity: Optional[str],
    state: Optional[str],
    district: Optional[str],
    market: Optional[str],
) -> list:

    filtered = []

    for record in records:
        if not matches_filter(record.get("commodity"), commodity):
            continue

        if not matches_filter(record.get("state"), state):
            continue

        if not matches_filter(record.get("district"), district):
            continue

        if not matches_filter(record.get("market"), market):
            continue

        filtered.append(record)

    return filtered


# ============================================================
# GET MARKET PRICES
# ============================================================

async def get_market_prices(
    commodity: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    market: Optional[str] = None,
    limit: int = 100,
) -> dict:

    if limit < 1 or limit > 1000:
        raise MarketAPIError(
            "Market price limit must be between 1 and 1000."
        )

    # --------------------------------------------------------
    # PRIMARY SOURCE
    # --------------------------------------------------------

    try:
        primary_records = await asyncio.to_thread(
            _fetch_primary_api,
            state,
            commodity,
        )

        filtered_records = filter_records(
            primary_records,
            commodity,
            state,
            district,
            market,
        )

        if not filtered_records:
            raise MarketAPIError(
                "No primary API records match the requested filters."
            )

        result_records = filtered_records[:limit]

        print(
            "MARKET SOURCE: Primary Mandi API",
            {
                "count": len(result_records),
                "total": len(filtered_records),
            },
        )

        return {
            "success": True,
            "count": len(result_records),
            "total": len(filtered_records),
            "records": result_records,
        }

    except MarketAPIError as error:
        print("PRIMARY MARKET API ERROR:", str(error))

    # --------------------------------------------------------
    # FALLBACK: GOVERNMENT CACHE
    # --------------------------------------------------------

    try:
        cache = load_market_cache()

        cached_records = []

        for record in cache.get("records", []):
            if not isinstance(record, dict):
                continue

            clean_record = normalize_market_record(record)

            if clean_record is not None:
                cached_records.append(clean_record)

        filtered_records = filter_records(
            cached_records,
            commodity,
            state,
            district,
            market,
        )

        result_records = filtered_records[:limit]

        if not result_records:
            raise MarketAPIError(
                "Neither the primary API nor the government cache "
                "provided valid matching records."
            )

        print(
            "MARKET SOURCE: Government cache fallback",
            {
                "count": len(result_records),
                "total": len(filtered_records),
                "updated_at": cache.get("updated_at"),
            },
        )

        return {
            "success": True,
            "count": len(result_records),
            "total": len(filtered_records),
            "records": result_records,
        }

    except MarketAPIError:
        raise

    except Exception as error:
        print("MARKET FALLBACK ERROR:", str(error))

        raise MarketAPIError(
            "Unable to retrieve market prices from available sources."
        ) from error