import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def export_fda_simulation_report(simulation_data: Dict[str, Any], output_prefix: str) -> Dict[str, str]:
    """Export simulation results to FDA-friendly JSON and PDF files.

    Args:
        simulation_data: Dictionary containing simulation results and metadata.
        output_prefix: Output file prefix. Directory will be created if needed.

    Returns:
        Dictionary with paths to generated 'json' and 'pdf' files.
    """
    prefix_path = Path(output_prefix)
    if prefix_path.parent:
        prefix_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    json_path = prefix_path.with_suffix(".json")
    pdf_path = prefix_path.with_suffix(".pdf")

    structured = {
        "schema_version": "1.0",
        "generated_at": timestamp,
        "simulation": simulation_data,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, default=str)

    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("FDA Simulation Report", styles["Title"]), Spacer(1, 12)]

    table_data = [["Field", "Value"]]
    for key, value in simulation_data.items():
        if isinstance(value, (dict, list)):
            formatted = json.dumps(value, indent=2, default=str)
        else:
            formatted = str(value)
        table_data.append([key, formatted])

    table = Table(table_data, colWidths=[150, 380])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(table)

    doc.build(story)

    return {"json": str(json_path), "pdf": str(pdf_path)}
