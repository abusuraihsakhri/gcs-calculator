"""Clinical and security regression tests for the GCS calculator."""

import csv
import pytest

from agents.base import AuditTrail
from gcs import calculate_gcs, calculate_gcs_p, parse_verbal_score, validate_component, process_csv


@pytest.mark.parametrize("e,v,m,total", [
    (4, 5, 6, 15), (1, 1, 1, 3), (2, 3, 4, 9), (3, 4, 6, 13),
])
def test_complete_scores(e, v, m, total):
    result = calculate_gcs(e, v, m)
    assert result["total"] == total
    assert result["verbal_display"] == str(v)


@pytest.mark.parametrize("verbal,intubated", [
    ("NT", False), ("1T", False), ("2T", False),
    (5, True), (1, True),
])
def test_verbal_unavailable_never_imputes_total(verbal, intubated):
    result = calculate_gcs(3, verbal, 4, intubated=intubated)
    assert result["verbal"] is None
    assert result["verbal_display"] == "NT"
    assert result["total"] is None
    assert result["severity"] is None
    with pytest.raises(ValueError):
        calculate_gcs_p(result["total"], 1)


@pytest.mark.parametrize("value", [True, 3.9, "2.0", None, "", "NaN"])
def test_eye_validation_rejects_nonintegers(value):
    with pytest.raises(ValueError):
        validate_component("eye", value, {1: "", 2: "", 3: "", 4: ""})


@pytest.mark.parametrize("prs", [True, 0.5, "1.5", None, "", "three"])
def test_prs_validation_rejects_invalid_values(prs):
    with pytest.raises(ValueError):
        calculate_gcs_p(12, prs)


def test_gcs_p_and_untestable_parsing():
    assert calculate_gcs_p(3, 2)["gcs_p"] == 1
    assert calculate_gcs_p(15, "1")["gcs_p"] == 14
    assert parse_verbal_score("NT") == (None, True)


def test_csv_requires_components(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("eye,verbal\n4,5\n", encoding="utf-8")
    with pytest.raises(ValueError, match="requires eye, verbal, and motor"):
        process_csv(source, tmp_path / "out.csv")


def test_csv_intubated_no_total_and_blank_pupils(tmp_path):
    source, output = tmp_path / "input.csv", tmp_path / "output.csv"
    source.write_text(
        "eye,verbal,motor,intubated,pupils\n"
        "3,1T,4,true,2\n"
        "4,5,6,false,0\n",
        encoding="utf-8",
    )
    rows = process_csv(source, output)
    assert rows[0]["gcs_total"] == ""
    assert rows[0]["verbal_display"] == "NT"
    assert rows[1]["gcs_total"] == 15
    assert rows[1]["gcs_p"] == 15
    with output.open(newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    assert records[0]["gcs_total"] == ""
    assert records[0]["gcs_p"] == ""


def test_audit_integrity_checks_signature_not_only_chain():
    trail = AuditTrail(secret_key="test-only-unique-key")
    entry = trail.log("operator", "test", "EVENT", {"x": 1})
    assert trail.verify_integrity()
    original = entry["actor"]
    entry["actor"] = "attacker"
    assert not trail.verify_integrity()
    entry["actor"] = original
    assert trail.verify_integrity()
    entry["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_csv_escapes_spreadsheet_formulas(tmp_path):
    source, output = tmp_path / "input.csv", tmp_path / "output.csv"
    source.write_text(
        "patient_id,eye,verbal,motor\n"
        "=HYPERLINK(1),4,5,6\n", encoding="utf-8"
    )
    rows = process_csv(source, output)
    assert rows[0]["patient_id"] == "=HYPERLINK(1)"
    with output.open(newline="", encoding="utf-8") as file:
        exported = list(csv.DictReader(file))
    assert exported[0]["patient_id"].startswith("'=")


def test_csv_rejects_extra_fields(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text("eye,verbal,motor\n4,5,6,7\n", encoding="utf-8")
    with pytest.raises(ValueError, match="more fields"):
        process_csv(source, tmp_path / "output.csv")
