"""Data ingestion pipelines for external sources like OpenPrescribing and OpenFDA."""

import asyncio
import logging
from typing import Any, Callable, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class BaseIngestor:
    """Base class for external data ingestion."""

    def __init__(self, source: str, endpoint: str, callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.source = source
        self.endpoint = endpoint
        self.callback = callback
        self._task: Optional[asyncio.Task] = None

    async def fetch(self) -> Dict[str, Any]:
        """Fetch raw data from the external API."""
        raise NotImplementedError

    def map_to_ontology(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw API data to Digital Twin schema. Override in subclasses."""
        return data

    async def sync(self) -> None:
        """Fetch, map and deliver data to the callback."""
        try:
            raw = await self.fetch()
            mapped = self.map_to_ontology(raw)
            if self.callback:
                self.callback(mapped)
            logger.info("Synced data from %s", self.source)
        except Exception as exc:
            logger.error("Failed to sync %s: %s", self.source, exc)

    def schedule_sync(self, frequency: str = "daily") -> None:
        """Schedule automatic synchronization.

        Args:
            frequency: Either ``'daily'`` or ``'weekly'``.
        """
        interval = 86400 if frequency == "daily" else 604800

        async def _loop() -> None:
            while True:
                await self.sync()
                await asyncio.sleep(interval)

        self._task = asyncio.create_task(_loop())


class OpenPrescribingIngestor(BaseIngestor):
    """Ingest prescribing analytics data from OpenPrescribing."""

    def __init__(self, callback: Optional[Callable[[Dict[str, Any]], None]] = None,
                 endpoint: str = "https://openprescribing.net/api/1.0/"):
        super().__init__("openprescribing", endpoint, callback)

    async def fetch(self) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()

        def _get() -> Dict[str, Any]:
            url = self.endpoint + "spending_by_ccg/"
            resp = requests.get(url, params={"code": "0503010B0", "format": "json"})
            resp.raise_for_status()
            return resp.json()

        return await loop.run_in_executor(None, _get)

    def map_to_ontology(self, data: Any) -> Dict[str, Any]:
        mapped = []
        for item in data:
            mapped.append({
                "chemical": item.get("chemical"),
                "period": item.get("date"),
                "quantity": item.get("items"),
                "cost": item.get("actual_cost"),
            })
        return {"prescriptions": mapped}


class OpenFDAIngestor(BaseIngestor):
    """Ingest safety event data from OpenFDA."""

    def __init__(self, callback: Optional[Callable[[Dict[str, Any]], None]] = None,
                 endpoint: str = "https://api.fda.gov/drug/event.json"):
        super().__init__("openfda", endpoint, callback)

    async def fetch(self) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()

        def _get() -> Dict[str, Any]:
            resp = requests.get(self.endpoint, params={"limit": 5})
            resp.raise_for_status()
            return resp.json()

        return await loop.run_in_executor(None, _get)

    def map_to_ontology(self, data: Dict[str, Any]) -> Dict[str, Any]:
        results = data.get("results", [])
        mapped = []
        for event in results:
            mapped.append({
                "safety_report_id": event.get("safetyreportid"),
                "received_date": event.get("receivedate"),
                "reactions": event.get("patient", {}).get("reaction", []),
            })
        return {"safety_reports": mapped}
