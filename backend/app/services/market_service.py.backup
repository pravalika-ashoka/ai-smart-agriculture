import json
from pathlib import Path
from typing import Optional


# ============================================================
# PATHS
# ============================================================

# Project structure:
#
# backend/
# ├── app/
# │   └── services/
# │       └── market_service.py
# │
# └── data/
#     └── market_cache.json
#
# parents[0] = services
# parents[1] = app
# parents[2] = backend

BASE_DIR = Path(__file__).resolve().parents[2]

CACHE_FILE = BASE_DIR / "data" / "market_cache.json"


# ============================================================
# GOVERNMENT MARKET DATA
# ============================================================

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

DATA_SOURCE = "Data.gov.in"


# ============================================================
# CUSTOM EXCEPTION
# ============================================================

class MarketAPIError(Exception):
    """
    Raised when cached government market data
    cannot be used.
    """

    pass


# ============================================================
# NORMALIZE MARKET RECORD
# ============================================================

def normalize_market_record(record: dict) -> dict:
    """
    Convert a cached Data.gov.in record into the structure
    expected by the frontend.
    """

    return {
        "state": record.get("state"),
        "district": record.get("district"),
        "market": record.get("market"),
        "commodity": record.get("commodity"),
        "variety": record.get("variety"),
        "grade": record.get("grade"),
        "arrival_date": record.get("arrival_date"),
        "min_price": record.get("min_price"),
        "max_price": record.get("max_price"),
        "modal_price": record.get("modal_price"),
    }


# ============================================================
# LOAD MARKET CACHE
# ============================================================

def load_market_cache() -> dict:
    """
    Load the latest government market-price data from
    backend/data/market_cache.json.

    The cache is updated automatically by GitHub Actions.
    """

    if not CACHE_FILE.exists():
        raise MarketAPIError(
            "Government market price cache is not available."
        )

    try:
        with CACHE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

    except json.JSONDecodeError as error:

        print(
            "MARKET CACHE INVALID JSON:",
            str(error),
        )

        raise MarketAPIError(
            "Government market price cache is invalid."
        ) from error

    except OSError as error:

        print(
            "MARKET CACHE READ ERROR:",
            str(error),
        )

        raise MarketAPIError(
            "Unable to read government market price cache."
        ) from error

    if not isinstance(data, dict):
        raise MarketAPIError(
            "Invalid government market price cache."
        )

    records = data.get(
        "records",
        [],
    )

    if not isinstance(records, list):
        raise MarketAPIError(
            "Invalid market price records in cache."
        )

    return data


# ============================================================
# SAFE STRING COMPARISON
# ============================================================

def matches_filter(
    value,
    filter_value: Optional[str],
) -> bool:
    """
    Case-insensitive exact comparison.

    Empty filter means no filtering.
    """

    if not filter_value:
        return True

    if value is None:
        return False

    return (
        str(value).strip().casefold()
        == filter_value.strip().casefold()
    )


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
    """
    Get the latest government mandi market prices.

    Data source:
        Data.gov.in

    The backend does NOT directly contact Data.gov.in.

    Instead, it reads the latest market_cache.json file,
    which is automatically updated by GitHub Actions.
    """

    # ========================================================
    # VALIDATE LIMIT
    # ========================================================

    if limit < 1 or limit > 1000:
        raise MarketAPIError(
            "Market price limit must be between 1 and 1000."
        )


    # ========================================================
    # LOAD CACHE
    # ========================================================

    cache = load_market_cache()


    # ========================================================
    # CACHE INFORMATION
    # ========================================================

    updated_at = cache.get(
        "updated_at"
    )

    source = cache.get(
        "source",
        DATA_SOURCE,
    )

    cached_total = cache.get(
        "total",
        0,
    )

    records = cache.get(
        "records",
        [],
    )


    # ========================================================
    # NORMALIZE RECORDS
    # ========================================================

    normalized_records = []

    for record in records:

        if not isinstance(record, dict):
            continue

        normalized_records.append(
            normalize_market_record(record)
        )


    # ========================================================
    # APPLY FILTERS
    # ========================================================

    filtered_records = []

    for record in normalized_records:

        if not matches_filter(
            record.get("commodity"),
            commodity,
        ):
            continue

        if not matches_filter(
            record.get("state"),
            state,
        ):
            continue

        if not matches_filter(
            record.get("district"),
            district,
        ):
            continue

        if not matches_filter(
            record.get("market"),
            market,
        ):
            continue

        filtered_records.append(record)


    # ========================================================
    # LIMIT RESULTS
    # ========================================================

    result_records = filtered_records[:limit]


    # ========================================================
    # TOTAL
    # ========================================================

    # When filters are used, return the number of records
    # matching those filters.
    #
    # Without filters, use the total supplied by the
    # government-data cache.

    has_filters = any([
        commodity and commodity.strip(),
        state and state.strip(),
        district and district.strip(),
        market and market.strip(),
    ])

    if has_filters:
        result_total = len(
            filtered_records
        )

    else:
        try:
            result_total = int(
                cached_total
            )

        except (
            TypeError,
            ValueError,
        ):
            result_total = len(
                normalized_records
            )


    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    print(
        "MARKET CACHE REQUEST:",
        {
            "commodity": commodity,
            "state": state,
            "district": district,
            "market": market,
            "limit": limit,
        },
    )

    print(
        "MARKET CACHE RESPONSE:",
        {
            "count": len(result_records),
            "total": result_total,
            "updated_at": updated_at,
            "source": source,
        },
    )


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "success": True,
        "count": len(result_records),
        "total": result_total,
        "records": result_records,
    }