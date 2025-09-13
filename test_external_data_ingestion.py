import pytest

from external_data_ingestion import map_prescribing_data, map_fda_data
from scenario_ui import ScenarioToggle


def test_map_prescribing_data():
    sample = [
        {"bnf_code": "0101010T0", "quantity": 10, "actual_cost": 2.5, "date": "2023-01-01"}
    ]
    mapped = map_prescribing_data(sample)
    assert mapped["source"] == "openprescribing"
    assert mapped["items"][0]["code"] == "0101010T0"


def test_map_fda_data():
    sample = {
        "results": [
            {
                "safetyreportid": "1",
                "receivedate": "20230101",
                "patient": {"reaction": [{"reactionmeddrapt": "Headache"}]},
            }
        ]
    }
    mapped = map_fda_data(sample)
    assert mapped["source"] == "openfda"
    assert mapped["reports"][0]["reactions"] == ["Headache"]


def test_toggle_scenario():
    toggle = ScenarioToggle()
    toggle.toggle("pricing")
    assert toggle.pricing is False
    toggle.toggle("pricing")
    assert toggle.pricing is True

