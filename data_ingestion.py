"""Utilities for integrating external prescribing and safety datasets.

This module provides lightweight helpers for fetching data from two public
APIs used in health‑care analytics:

* `OpenPrescribing` – aggregated prescribing statistics from the NHS.
* `OpenFDA` – adverse event reports for drugs collected by the FDA.

The real APIs can be accessed at runtime, but the functions are designed to be
Easily mockable so unit tests do not require network access.  A thin schema
mapping helper is also provided to align the heterogeneous data into a simple
structure used by the digital twin experiments.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional

import json
import requests

OPEN_PRESCRIBING_URL = "https://openprescribing.net/api/1.0/spending/"
OPEN_FDA_URL = "https://api.fda.gov/drug/event.json"


# ---------------------------------------------------------------------------
# Data ingestion helpers
# ---------------------------------------------------------------------------

def fetch_open_prescribing(*, date: Optional[str] = None, ccg: Optional[str] = None,
                           session: Optional[requests.Session] = None) -> Dict[str, Any]:
    """Fetch prescribing statistics from the OpenPrescribing API.

    Parameters are intentionally small; callers can provide additional
    parameters via the ``session`` if needed.  The function returns the decoded
    JSON payload.
    """

    params = {"format": "json"}
    if date:
        params["date"] = date
    if ccg:
        params["org"] = ccg

    sess = session or requests.Session()
    response = sess.get(OPEN_PRESCRIBING_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_openfda_drug_events(*, search: str, limit: int = 100,
                              session: Optional[requests.Session] = None) -> Dict[str, Any]:
    """Fetch adverse event reports from OpenFDA.

    ``search`` follows the standard OpenFDA query syntax, e.g. ``"patient.drug.medicinalproduct:ASPIRIN"``.
    """

    params = {"search": search, "limit": limit}
    sess = session or requests.Session()
    response = sess.get(OPEN_FDA_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Synchronisation helpers
# ---------------------------------------------------------------------------

def next_sync_time(interval: str) -> datetime:
    """Return the next timestamp a sync job should run.

    Parameters
    ----------
    interval:
        Either ``"daily"`` or ``"weekly"``.
    """

    now = datetime.utcnow()
    if interval == "daily":
        return now + timedelta(days=1)
    if interval == "weekly":
        return now + timedelta(weeks=1)
    raise ValueError("interval must be 'daily' or 'weekly'")


# ---------------------------------------------------------------------------
# Schema mapping
# ---------------------------------------------------------------------------

def align_to_ontology(prescribing: Iterable[Dict[str, Any]],
                      safety: Iterable[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Align raw prescribing and safety datasets into a tiny common schema.

    Parameters
    ----------
    prescribing:
        Iterable of records from OpenPrescribing ``spending`` endpoint.
    safety:
        Iterable of FDA adverse event reports.
    """

    mapped_prescribing = [
        {
            "drug_code": record.get("bnf_code"),
            "items": record.get("items"),
            "quantity": record.get("quantity"),
        }
        for record in prescribing
    ]

    mapped_safety = [
        {
            "safety_report_id": report.get("safetyreportid"),
            "reactions": report.get("patient", {}).get("reaction", []),
        }
        for report in safety
    ]

    return {"prescriptions": mapped_prescribing, "adverse_events": mapped_safety}


# ---------------------------------------------------------------------------
# Scenario configuration (UI toggle placeholder)
# ---------------------------------------------------------------------------

@dataclass
class ScenarioInputs:
    pricing: Optional[float] = None
    utilization: Optional[float] = None
    policy: Optional[str] = None


def apply_scenario(inputs: ScenarioInputs) -> Dict[str, Any]:
    """Return a serialisable representation of user provided scenario inputs.

    A real UI would collect these inputs interactively.  For the kata we simply
    bundle the values into a dictionary which can be consumed by simulation
    routines.
    """

    return {
        "pricing": inputs.pricing,
        "utilization": inputs.utilization,
        "policy": inputs.policy,
    }


# ---------------------------------------------------------------------------
# FDA style report export (stretch goal)
# ---------------------------------------------------------------------------


def export_fda_report(data: Dict[str, Any], path: str, *, fmt: str = "json") -> None:
    """Export simulation results to either JSON or a minimal PDF.

    The PDF export uses a very small dependency (``reportlab``) if available;
    otherwise a plain text representation is written with a ``.pdf`` extension.
    """

    fmt = fmt.lower()
    if fmt == "json":
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
        return

    if fmt == "pdf":  # pragma: no cover - optional dependency
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except Exception:
            # Fallback: write simple text if reportlab is missing
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(data, indent=2, sort_keys=True))
            return

        c = canvas.Canvas(path, pagesize=letter)
        textobject = c.beginText(40, 750)
        for line in json.dumps(data, indent=2, sort_keys=True).splitlines():
            textobject.textLine(line)
        c.drawText(textobject)
        c.showPage()
        c.save()
        return

    raise ValueError("Unsupported format: {fmt}")
