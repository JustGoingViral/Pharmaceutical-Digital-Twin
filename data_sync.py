"""Asynchronous data synchronization with external prescribing and safety datasets."""

import asyncio
import json
import logging
import os
from datetime import datetime

import aiohttp

logger = logging.getLogger(__name__)

OPENPRESCRIBING_URL = "https://openprescribing.net/api/1.0/spending/?code=0412000AA"
OPENFDA_URL = "https://api.fda.gov/drug/event.json?limit=1"


def _save_data(source: str, data: dict) -> None:
    """Persist fetched data to disk grouped by source."""
    directory = os.path.join("data", source)
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{datetime.utcnow().date().isoformat()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    logger.info("Saved %s data to %s", source, path)


async def _fetch_json(session: aiohttp.ClientSession, url: str) -> dict:
    """Fetch JSON payload from a URL."""
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


async def sync_openprescribing() -> None:
    """Fetch latest analytics from OpenPrescribing."""
    async with aiohttp.ClientSession() as session:
        data = await _fetch_json(session, OPENPRESCRIBING_URL)
        _save_data("openprescribing", data)


async def sync_openfda() -> None:
    """Fetch latest adverse event data from OpenFDA."""
    async with aiohttp.ClientSession() as session:
        data = await _fetch_json(session, OPENFDA_URL)
        _save_data("openfda", data)


async def auto_sync_openprescribing(interval_hours: int = 24) -> None:
    """Continuously sync OpenPrescribing data every N hours."""
    while True:
        try:
            await sync_openprescribing()
        except Exception as exc:  # pragma: no cover - logging only
            logger.error("OpenPrescribing sync failed: %s", exc)
        await asyncio.sleep(interval_hours * 3600)


async def auto_sync_openfda(interval_days: int = 7) -> None:
    """Continuously sync OpenFDA data every N days."""
    while True:
        try:
            await sync_openfda()
        except Exception as exc:  # pragma: no cover - logging only
            logger.error("OpenFDA sync failed: %s", exc)
        await asyncio.sleep(interval_days * 86400)


async def start_auto_sync() -> None:
    """Kick off background tasks for both data sources."""
    asyncio.create_task(auto_sync_openprescribing())
    asyncio.create_task(auto_sync_openfda())
