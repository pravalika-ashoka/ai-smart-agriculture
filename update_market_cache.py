import json
import os
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# --------------------------------------------------
# Configuration
# --------------------------------------------------

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

API_URL = (
    "https://api.data.gov.in/resource/"
    + RESOURCE_ID
)

STATE = "Karnataka"
PAGE_SIZE = 1000
MAX_RECORDS = 50000
MAX_RETRIES = 5
REQUEST_TIMEOUT = 60

PROJECT_DIR = Path(__file__).resolve().parent
CACHE_PATH = PROJECT_DIR / "backend" / "data" / "market_cache.json"


# --------------------------------------------------
# API key
# --------------------------------------------------

API_KEY = os.environ.get("DATA_GOV_API_KEY", "").strip()

if not API_KEY:
    raise RuntimeError(
        "DATA_GOV_API_KEY is missing. "
        "Set it as an environment variable before running."
    )


# --------------------------------------------------
# Fetch one page
# --------------------------------------------------

def fetch_page(offset: int, limit: int) -> dict:
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "offset": offset,
    }

    url = API_URL + "?" + urlencode(params)
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        request = Request(
            url,
            headers={
                "User-Agent": "AI-Smart-Agriculture/1.0",
                "Accept": "application/json",
            },
        )

        try:
            print(
                f"Fetching offset={offset}, "
                f"limit={limit}, attempt={attempt}/{MAX_RETRIES}"
            )

            with urlopen(
                request,
                timeout=REQUEST_TIMEOUT,
            ) as response:
                payload = response.read()

            data = json.loads(payload.decode("utf-8"))

            if not isinstance(data, dict):
                raise RuntimeError("Unexpected API response format.")

            if data.get("error"):
                raise RuntimeError(
                    "Data.gov.in API error: "
                    + str(data["error"])[:300]
                )

            records = data.get("records")

            if not isinstance(records, list):
                raise RuntimeError(
                    "API response does not contain a valid records list."
                )

            return data

        except HTTPError as error:
            last_error = error

            print(f"HTTP error: {error.code}")

            if error.code not in (
                408, 425, 429, 500, 502, 503, 504
            ):
                raise RuntimeError(
                    f"Non-retryable HTTP error: {error.code}"
                ) from error

        except (
            URLError,
            TimeoutError,
            socket.timeout,
            ConnectionError,
        ) as error:
            last_error = error
            print(f"Connection error: {error!r}")

        if attempt < MAX_RETRIES:
            wait_seconds = min(5 * (2 ** (attempt - 1)), 60)
            print(f"Retrying in {wait_seconds} seconds...")
            time.sleep(wait_seconds)

    raise RuntimeError(
        f"Could not retrieve offset {offset} after "
        f"{MAX_RETRIES} attempts. Last error: {last_error!r}"
    ) from last_error


# --------------------------------------------------
# Fetch all pages
# --------------------------------------------------

def fetch_all_records() -> list[dict]:
    all_records = []
    offset = 0

    while offset < MAX_RECORDS:
        limit = min(PAGE_SIZE, MAX_RECORDS - offset)

        data = fetch_page(offset, limit)
        records = data["records"]

        print(f"Records received: {len(records)}")

        if not records:
            break

        all_records.extend(
            record
            for record in records
            if isinstance(record, dict)
        )

        offset += len(records)

        print(f"Total records collected: {len(all_records)}")

        if len(records) < limit:
            print("Final page reached.")
            break

        time.sleep(1)

    if not all_records:
        raise RuntimeError(
            "No market records retrieved. Existing cache preserved."
        )

    return all_records


# --------------------------------------------------
# Filter Karnataka records
# --------------------------------------------------

def filter_karnataka(records: list[dict]) -> list[dict]:
    fields = (
        "state",
        "district",
        "market",
        "commodity",
        "variety",
        "grade",
        "arrival_date",
        "min_price",
        "max_price",
        "modal_price",
    )

    filtered = []

    for record in records:
        state = str(record.get("state") or "").strip()

        if state.casefold() != STATE.casefold():
            continue

        filtered.append({
            field: record.get(field)
            for field in fields
        })

    if not filtered:
        raise RuntimeError(
            "No Karnataka records found. Existing cache preserved."
        )

    unique_records = []
    seen = set()

    for record in filtered:
        key = tuple(
            record.get(field)
            for field in fields
        )

        if key in seen:
            continue

        seen.add(key)
        unique_records.append(record)

    if not unique_records:
        raise RuntimeError(
            "No unique records remain. Existing cache preserved."
        )

    return unique_records


# --------------------------------------------------
# Write cache safely
# --------------------------------------------------

def update_cache(records: list[dict]) -> None:
    cache = {
        "success": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Data.gov.in",
        "resource_id": RESOURCE_ID,
        "state": STATE,
        "total": len(records),
        "records": records,
    }

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = CACHE_PATH.with_suffix(".json.tmp")

    temporary_path.write_text(
        json.dumps(
            cache,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # Validate the temporary file before replacing the existing cache.
    with temporary_path.open("r", encoding="utf-8") as file:
        verification = json.load(file)

    if (
        verification.get("success") is not True
        or not isinstance(verification.get("records"), list)
        or verification.get("total") != len(records)
    ):
        temporary_path.unlink(missing_ok=True)
        raise RuntimeError(
            "Cache validation failed. Existing cache preserved."
        )

    temporary_path.replace(CACHE_PATH)

    print("\nMarket cache updated successfully.")
    print(f"Records stored: {len(records)}")
    print(f"Cache path: {CACHE_PATH}")


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("=" * 60)
    print("AI SMART AGRICULTURE — MARKET CACHE UPDATE")
    print("=" * 60)

    all_records = fetch_all_records()
    print(f"\nTotal API records fetched: {len(all_records)}")

    karnataka_records = filter_karnataka(all_records)

    districts = {
        record["district"]
        for record in karnataka_records
        if record.get("district")
    }

    markets = {
        record["market"]
        for record in karnataka_records
        if record.get("market")
    }

    commodities = {
        record["commodity"]
        for record in karnataka_records
        if record.get("commodity")
    }

    print(f"Karnataka records: {len(karnataka_records)}")
    print(f"Districts: {len(districts)}")
    print(f"Markets: {len(markets)}")
    print(f"Commodities: {len(commodities)}")

    update_cache(karnataka_records)


if __name__ == "__main__":
    main()