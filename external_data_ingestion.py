"""External data ingestion pipelines for OpenPrescribing and OpenFDA.

This module provides utility functions to retrieve prescribing analytics
from the OpenPrescribing API and real‑world evidence (RWE) datasets from
OpenFDA.  Retrieved data are mapped to the internal Digital Twin
ontology and can be scheduled for periodic synchronisation.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any, Callable, Dict, Iterable, List, Optional

import requests

# API endpoints
OPENPRESCRIBING_API = "https://openprescribing.net/api/1.0/spending_by_practice"
OPENFDA_API = "https://api.fda.gov/drug/event.json"


def fetch_openprescribing(ccg: str, measure: str) -> List[Dict[str, Any]]:
    """Fetch prescribing analytics for a Clinical Commissioning Group.

    Parameters
    ----------
    ccg: str
        The CCG identifier (e.g. ``"10Q"``).
    measure: str
        Measure name such as ``"cost"`` or ``"quantity"``.
    """

    params = {"ccg": ccg, "measure": measure}
    resp = requests.get(OPENPRESCRIBING_API, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_openfda(drug_name: str, limit: int = 1) -> Dict[str, Any]:
    """Fetch adverse event reports for a drug from OpenFDA."""

    params = {
        "search": f"patient.drug.medicinalproduct:\"{drug_name}\"",
        "limit": limit,
    }
    resp = requests.get(OPENFDA_API, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def map_prescribing_data(data: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Map OpenPrescribing data to the Digital Twin schema."""

    items = [
        {
            "code": row.get("bnf_code"),
            "quantity": row.get("quantity"),
            "cost": row.get("actual_cost"),
            "date": row.get("date"),
        }
        for row in data
    ]
    return {"source": "openprescribing", "items": items}


def map_fda_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map OpenFDA event data to the Digital Twin schema."""

    reports = []
    for result in data.get("results", []):
        reactions = [
            rx.get("reactionmeddrapt")
            for rx in result.get("patient", {}).get("reaction", [])
        ]
        reports.append(
            {
                "safety_report_id": result.get("safetyreportid"),
                "received_date": result.get("receivedate"),
                "reactions": reactions,
            }
        )
    return {"source": "openfda", "reports": reports}


def _default_store(target: List[Dict[str, Any]], payload: Dict[str, Any]) -> None:
    """Default callback to store synced payloads in a list."""

    target.append(payload)


def schedule_sync(
    interval: timedelta,
    fetch: Callable[..., Any],
    mapper: Callable[[Any], Dict[str, Any]],
    callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    *args: Any,
    **kwargs: Any,
) -> Callable[[], None]:
    """Schedule periodic synchronisation.

    Returns a function that cancels the scheduled task when called.
    """

    loop = asyncio.get_event_loop()
    storage: List[Dict[str, Any]] = []

    if callback is None:
        callback = lambda payload: _default_store(storage, payload)

    async def _runner() -> None:
        while True:
            data = fetch(*args, **kwargs)
            mapped = mapper(data)
            callback(mapped)
            await asyncio.sleep(interval.total_seconds())

    task = loop.create_task(_runner())

    def cancel() -> None:
        task.cancel()

    return cancel

