import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from datetime import datetime, timezone
from pathlib import Path


RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
API_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_FILE = PROJECT_ROOT / "data" / "market_cache.json"

STATE_NAME = "Karnataka"
PAGE_SIZE = 1000
MAX_RETRIES = 5


def fetch_page(api_key: str, offset: int) -> dict:
    params = {
        "api-key": api_key,
        "format": "json",
        "limit": PAGE_SIZE,
        "offset": offset,
    }

    url = f"{API_URL}?{urllib.parse.urlencode(params)}"

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AI-Smart-Agriculture/1.0",
            "Accept": "application/json",
        },
    )

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(
                request,
                timeout=60,
            ) as response:
                payload = json.loads(
                    response.read().decode("utf-8")
                )

            if not isinstance(payload, dict):
                raise RuntimeError("Invalid API response.")

            if payload.get("status") != "ok":
                raise RuntimeError(
                    "Data.gov.in did not return status 'ok'."
                )

            if not isinstance(payload.get("records"), list):
                raise RuntimeError(
                    "API response does not contain valid records."
                )

            return payload

        except urllib.error.HTTPError as exc:
            # Authentication or request errors should not be retried.
            if exc.code in (400, 401, 403):
                raise RuntimeError(
                    f"Data.gov.in rejected the request: HTTP {exc.code}"
                ) from exc

            last_error = exc

        except (
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
        ) as exc:
            last_error = exc

        if attempt < MAX_RETRIES:
            delay = min(2 ** attempt, 30)
            print(
                f"Request failed at offset {offset}. "
                f"Retrying in {delay}s "
                f"({attempt}/{MAX_RETRIES})..."
            )
            time.sleep(delay)

    raise RuntimeError(
        f"Unable to fetch offset {offset} after "
        f"{MAX_RETRIES} attempts: {last_error}"
    )


def normalize_record(record: dict) -> dict:
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

    return {field: record.get(field) for field in fields}


def main() -> None:
    api_key = os.environ.get("DATA_GOV_API_KEY", "").strip()

    if not api_key:
        raise SystemExit(
            "DATA_GOV_API_KEY is missing. Set it in PowerShell first."
        )

    print("Fetching official Data.gov.in mandi records...")

    all_records = []
    offset = 0
    reported_total = None

    while True:
        payload = fetch_page(api_key, offset)
        records = payload["records"]

        if reported_total is None:
            reported_total = int(payload.get("total", 0))
            print(f"Official dataset total: {reported_total}")

        if not records:
            break

        all_records.extend(records)

        print(
            f"Fetched {len(all_records)} records "
            f"of approximately {reported_total}..."
        )

        offset += len(records)

        if offset >= reported_total:
            break

        # Avoid a tight request loop.
        time.sleep(0.2)

    # Keep only Karnataka records.
    karnataka_records = [
        normalize_record(record)
        for record in all_records
        if isinstance(record, dict)
        and str(record.get("state", "")).strip().casefold()
        == STATE_NAME.casefold()
    ]

    if not karnataka_records:
        raise RuntimeError(
            "No Karnataka records were found. "
            "The existing cache has not been changed."
        )

    # Validate the data before replacing the existing cache.
    for record in karnataka_records:
        if not record.get("commodity") or not record.get("state"):
            raise RuntimeError(
                "Invalid market record found. "
                "The existing cache has not been changed."
            )

    cache = {
        "success": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Data.gov.in",
        "resource_id": RESOURCE_ID,
        "state": STATE_NAME,
        "total": len(karnataka_records),
        "records": karnataka_records,
    }

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = CACHE_FILE.with_suffix(".json.tmp")

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(
                cache,
                file,
                ensure_ascii=False,
                indent=2,
            )
            file.write("\n")

        # Replace the cache only after a complete successful fetch.
        temporary_file.replace(CACHE_FILE)

    finally:
        if temporary_file.exists():
            temporary_file.unlink()

    print("\nMarket cache updated successfully.")
    print(f"Cache file: {CACHE_FILE}")
    print(f"Karnataka records: {len(karnataka_records)}")
    print(f"Updated at: {cache['updated_at']}")


if __name__ == "__main__":
    main()