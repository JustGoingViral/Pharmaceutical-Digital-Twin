"""Export simulation reports in FDA-friendly formats."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:  # PDF support is optional
    from fpdf import FPDF  # type: ignore
except Exception:  # pragma: no cover - library may be missing
    FPDF = None


def export_fda_report(results: Dict[str, Any], json_path: str, pdf_path: Optional[str] = None) -> None:
    """Write results to ``json_path`` and optionally create a simple PDF report."""
    Path(json_path).write_text(json.dumps(results, indent=2))

    if pdf_path and FPDF is not None:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for key, value in results.items():
            pdf.multi_cell(0, 10, f"{key}: {value}")
        pdf.output(pdf_path)
