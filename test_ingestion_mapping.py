from datetime import datetime

from data_ingestion import (
    ScenarioInputs,
    align_to_ontology,
    apply_scenario,
    next_sync_time,
)


def test_align_to_ontology():
    prescribing = [{"bnf_code": "ABC", "items": 10, "quantity": 20}]
    safety = [{"safetyreportid": "R1", "patient": {"reaction": ["headache"]}}]
    mapped = align_to_ontology(prescribing, safety)
    assert mapped["prescriptions"][0]["drug_code"] == "ABC"
    assert mapped["adverse_events"][0]["safety_report_id"] == "R1"


def test_apply_scenario():
    inputs = ScenarioInputs(pricing=9.99, utilization=0.8, policy="baseline")
    cfg = apply_scenario(inputs)
    assert cfg["policy"] == "baseline"
    assert cfg["pricing"] == 9.99
    assert cfg["utilization"] == 0.8


def test_next_sync_time():
    now = datetime.utcnow()
    delta_daily = next_sync_time("daily") - now
    assert 0.9 < delta_daily.total_seconds() / 86400 < 1.1
    delta_weekly = next_sync_time("weekly") - now
    assert 6.9 < delta_weekly.total_seconds() / 86400 < 7.1
