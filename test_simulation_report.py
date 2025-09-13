import json
import os
from simulation_report import export_fda_simulation_report


def test_export_fda_simulation_report(tmp_path):
    data = {
        "scenario_id": "TEST1",
        "yield": 0.97,
        "anomalies": [],
    }
    prefix = tmp_path / "sim_report"
    files = export_fda_simulation_report(data, str(prefix))

    assert os.path.exists(files["json"])  # JSON file created
    assert os.path.exists(files["pdf"])  # PDF file created

    with open(files["json"], "r", encoding="utf-8") as f:
        content = json.load(f)
    assert content["simulation"]["scenario_id"] == "TEST1"
