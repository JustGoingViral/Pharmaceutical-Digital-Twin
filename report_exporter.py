"""Utilities to export simulation results in FDA‑friendly formats."""

from __future__ import annotations

import json
from typing import Dict

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def export_fda_report(data: Dict, base_path: str) -> Dict[str, str]:
    """Export simulation results to JSON and PDF files.

    Parameters
    ----------
    data: Dict
        Simulation results already mapped to the Digital Twin ontology.
    base_path: str
        Path without extension where files will be written.

    Returns
    -------
    Dict[str, str]
        Mapping of format to the generated file path.
    """

    json_path = f"{base_path}.json"
    pdf_path = f"{base_path}.pdf"

    # Write JSON representation
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Basic PDF rendering
    c = canvas.Canvas(pdf_path, pagesize=letter)
    text = c.beginText(40, 750)
    text.textLine("FDA Simulation Report")
    for key, value in data.items():
        text.textLine(f"{key}: {value}")
    c.drawText(text)
    c.showPage()
    c.save()

    return {"json": json_path, "pdf": pdf_path}

