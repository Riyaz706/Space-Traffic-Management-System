"""
Update Data Orchestrator
1) Fetch raw live data -> data/raw_satellite_data.json
2) Process to canonical schema -> data/processed_satellite_data.json
3) Archive existing fake_satellite_data.json
4) Replace fake_satellite_data.json with processed version
"""

import asyncio
import os
import shutil
from datetime import datetime

from src.data_collection.data_fetcher import DataFetcher
from src.data_collection.data_pipeline import DataPipeline


ARCHIVE_DIR = "data/archive"
FAKE_PATH = "data/fake_satellite_data.json"
PROCESSED_PATH = "data/processed_satellite_data.json"


def archive_existing() -> None:
    if not os.path.exists(FAKE_PATH):
        return
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base = os.path.basename(FAKE_PATH)
    archive_path = os.path.join(ARCHIVE_DIR, f"{ts}_{base}")
    shutil.copy2(FAKE_PATH, archive_path)


def replace_with_processed() -> None:
    if not os.path.exists(PROCESSED_PATH):
        raise FileNotFoundError(PROCESSED_PATH)
    # Remove old fake file (if exists) then copy processed over it
    if os.path.exists(FAKE_PATH):
        os.remove(FAKE_PATH)
    shutil.copy2(PROCESSED_PATH, FAKE_PATH)


async def run_async(target_count: int = 50) -> None:
    # 1) Fetch raw
    async with DataFetcher() as fetcher:
        await fetcher.fetch(target_count=target_count)

    # 2) Process to canonical schema
    DataPipeline().run()

    # 3) Archive existing and 4) replace
    archive_existing()
    replace_with_processed()


def main() -> None:
    asyncio.run(run_async(target_count=50))


if __name__ == "__main__":
    main()


