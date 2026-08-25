#!/usr/bin/env python3
"""
Tests for the Glasgow Coma Scale Calculator.

Covers:
- All individual component scores (Eye, Verbal, Motor)
- Normal GCS (15)
- Mild brain injury (13-14)
- Moderate brain injury (9-12)
- Severe brain injury / coma (3-8)
- Deep coma (3)
- Intubated patients (verbal 1T)
- GCS-P (GCS-Pupil) calculation
- Pediatric verbal scale
- Input validation / error handling
- CSV batch processing
- CLI argument parsing
"""

import csv
import json
import os
import sys
import tempfile
import unittest

from gcs import (
    calculate_gcs,
    calculate_gcs_p,
    classify_severity,
    format_result,
    parse_verbal_score,
    process_csv,
    validate_component,
    EYE_SCORES,
    VERBAL_SCORES,
    MOTOR_SCORES,
    PEDIATRIC_VERBAL_SCORES,
    main as cli_main,
)


class TestEyeOpeningScores(unittest.TestCase):
    """Test all Eye Opening (E) component scores."""

    def test_eye_4_spontaneous(self):
        r = calculate_gcs(4, 5, 6)
        self.assertEqual(r["eye"], 4)
        self.assertEqual(r["eye_description"], "Spontaneous")

    def test_eye_3_to_voice(self):
        r = calculate_gcs(3, 5, 6)
        self.assertEqual(r["eye"], 3)
        self.assertEqual(r["eye_description"], "To voice/command")

    def test_eye_2_to_pain(self):
        r = calculate_gcs(2, 5, 6)
        self.assertEqual(r["eye"], 2)
        self.assertEqual(r["eye_description"], "To pressure/pain")

    def test_eye_1_none(self):
        r = calculate_gcs(1, 5, 6)
        self.assertEqual(r["eye"], 1)
        self.assertEqual(r["eye_description"], "None")


class TestVerbalResponseScores(unittest.TestCase):
    """Test all Verbal Response (V) component scores."""

    def test_verbal_5_oriented(self):
        r = calculate_gcs(4, 5, 6)
        self.assertEqual(r["verbal"], 5)
        self.assertEqual(r["verbal_description"], "Oriented")

    def test_verbal_4_confused(self):
        r = calculate_gcs(4, 4, 6)
        self.assertEqual(r["verbal"], 4)
        self.assertEqual(r["verbal_description"], "Confused conversation")

    def test_verbal_3_inappropriate(self):
        r = calculate_gcs(4, 3, 6)
        self.assertEqual(r["verbal"], 3)
        self.assertEqual(r["verbal_description"], "Inappropriate words")

    def test_verbal_2_incomprehensible(self):
        r = calculate_gcs(4, 2, 6)
        self.assertEqual(r["verbal"], 2)
        self.assertEqual(r["verbal_description"], "Incomprehensible sounds")

    def test_verbal_1_none(self):
        r = calculate_gcs(4, 1, 6)
        self.assertEqual(r["verbal"], 1)
        self.assertEqual(r["verbal_description"], "None")


class TestMotorResponseScores(unittest.TestCase):
    """Test all Motor Response (M) component scores."""

    def test_motor_6_obeys(self):
        r = calculate_gcs(4, 5, 6)
        self.assertEqual(r["motor"], 6)
        self.assertEqual(r["motor_description"], "Obeys commands")

    def test_motor_5_localizes(self):
        r = calculate_gcs(4, 5, 5)
        self.assertEqual(r["motor"], 5)
        self.assertEqual(r["motor_description"], "Localizes pain")

    def test_motor_4_withdrawal(self):
        r = calculate_gcs(4, 5, 4)
        self.assertEqual(r["motor"], 4)
        self.assertEqual(r["motor_description"], "Withdrawal (flexion)")

    def test_motor_3_abnormal_flexion(self):
        r = calculate_gcs(4, 5, 3)
        self.assertEqual(r["motor"], 3)
        self.assertEqual(r["motor_description"], "Abnormal flexion (decorticate)")

    def test_motor_2_extension(self):
        r = calculate_gcs(4, 5, 2)
        self.assertEqual(r["motor"], 2)
        self.assertEqual(r["motor_description"], "Extension (decerebrate)")

    def test_motor_1_none(self):
        r = calculate_gcs(4, 5, 1)
        self.assertEqual(r["motor"], 1)
        self.assertEqual(r["motor_description"], "None")


class TestNormalGCS(unittest.TestCase):
    """Test GCS = 15 (Normal)."""

    def test_gcs_15(self):
        r = calculate_gcs(4, 5, 6)
        self.assertEqual(r["total"], 15)
        self.assertEqual(r["severity"], "Normal")

    def test_gcs_15_components(self):
        r = calculate_gcs(4, 5, 6)
        self.assertEqual(r["eye"], 4)
        self.assertEqual(r["verbal"], 5)
        self.assertEqual(r["motor"], 6)


class TestMildBrainInjury(unittest.TestCase):
    """Test GCS 13-14 (Mild brain injury)."""

    def test_gcs_14(self):
        r = calculate_gcs(4, 4, 6)
        self.assertEqual(r["total"], 14)
        self.assertEqual(r["severity"], "Mild brain injury")

    def test_gcs_13(self):
        r = calculate_gcs(4, 4, 5)
        self.assertEqual(r["total"], 13)
        self.assertEqual(r["severity"], "Mild brain injury")

    def test_gcs_13_alternate(self):
        r = calculate_gcs(3, 4, 6)
        self.assertEqual(r["total"], 13)
        self.assertEqual(r["severity"], "Mild brain injury")


class TestModerateBrainInjury(unittest.TestCase):
    """Test GCS 9-12 (Moderate brain injury)."""

    def test_gcs_12(self):
        r = calculate_gcs(3, 4, 5)
        self.assertEqual(r["total"], 12)
        self.assertEqual(r["severity"], "Moderate brain injury")

    def test_gcs_10(self):
        r = calculate_gcs(3, 3, 4)
        self.assertEqual(r["total"], 10)
        self.assertEqual(r["severity"], "Moderate brain injury")

    def test_gcs_9(self):
        r = calculate_gcs(2, 3, 4)
        self.assertEqual(r["total"], 9)
        self.assertEqual(r["severity"], "Moderate brain injury")


class TestSevereBrainInjury(unittest.TestCase):
    """Test GCS 3-8 (Severe brain injury / coma)."""

    def test_gcs_8(self):
        r = calculate_gcs(2, 2, 4)
        self.assertEqual(r["total"], 8)
        self.assertEqual(r["severity"], "Severe brain injury (coma)")

    def test_gcs_6(self):
        r = calculate_gcs(1, 2, 3)
        self.assertEqual(r["total"], 6)
        self.assertEqual(r["severity"], "Severe brain injury (coma)")

    def test_gcs_3_deep_coma(self):
        r = calculate_gcs(1, 1, 1)
        self.assertEqual(r["total"], 3)
        self.assertEqual(r["severity"], "Severe brain injury (coma)")

    def test_gcs_3_components_all_minimum(self):
        r = calculate_gcs(1, 1, 1)
        self.assertEqual(r["eye"], 1)
        self.assertEqual(r["verbal"], 1)
        self.assertEqual(r["motor"], 1)
        self.assertEqual(r["total"], 3)


class TestIntubatedPatient(unittest.TestCase):
    """Test intubated patient handling (verbal = 1T)."""

    def test_intubated_verbal_1t(self):
        r = calculate_gcs(3, "1T", 4)
        self.assertEqual(r["verbal"], 1)
        self.assertEqual(r["verbal_display"], "1T")
        self.assertTrue(r["is_intubated"])
        self.assertEqual(r["total"], 8)  # 3 + 1 + 4

    def test_intubated_verbal_1t_string(self):
        r = calculate_gcs(4, "1T", 6)
        self.assertEqual(r["verbal"], 1)
        self.assertEqual(r["verbal_display"], "1T")
        self.assertTrue(r["is_intubated"])
        self.assertEqual(r["total"], 11)  # 4 + 1 + 6

    def test_intubated_flag_sets_intubated(self):
        """When --intubated flag is set, verbal is reported as 1T."""
        r = calculate_gcs(3, 1, 4, intubated=True)
        self.assertTrue(r["is_intubated"])
        self.assertEqual(r["verbal_display"], "1T")

    def test_intubated_format_output(self):
        r = calculate_gcs(3, "1T", 4)
        output = format_result(r)
        self.assertIn("1T", output)
        self.assertIn("intubated", output.lower())

    def test_intubated_with_gcs_p(self):
        r = calculate_gcs(3, "1T", 4)
        gcs_p = calculate_gcs_p(r["total"], 1)
        self.assertEqual(gcs_p["gcs_p"], 7)  # 8 - 1

    def test_parse_verbal_score_1t(self):
        v, intubated = parse_verbal_score("1T")
        self.assertEqual(v, 1)
        self.assertTrue(intubated)

    def test_parse_verbal_score_2t(self):
        v, intubated = parse_verbal_score("2T")
        self.assertEqual(v, 2)
        self.assertTrue(intubated)

    def test_parse_verbal_score_normal(self):
        v, intubated = parse_verbal_score("5")
        self.assertEqual(v, 5)
        self.assertFalse(intubated)

    def test_parse_verbal_score_case_insensitive(self):
        v, intubated = parse_verbal_score("1t")
        self.assertEqual(v, 1)
        self.assertTrue(intubated)


class TestGCSPupilScore(unittest.TestCase):
    """Test GCS-P (GCS-Pupil) score calculation."""

    def test_gcs_p_both_pupils_react(self):
        gcs_p = calculate_gcs_p(15, 0)
        self.assertEqual(gcs_p["gcs_p"], 15)
        self.assertEqual(gcs_p["prs"], 0)
        self.assertEqual(gcs_p["prs_description"], "Both pupils react")

    def test_gcs_p_one_pupil_reacts(self):
        gcs_p = calculate_gcs_p(15, 1)
        self.assertEqual(gcs_p["gcs_p"], 14)
        self.assertEqual(gcs_p["prs"], 1)
        self.assertEqual(gcs_p["prs_description"], "One pupil reacts")

    def test_gcs_p_neither_pupil_reacts(self):
        gcs_p = calculate_gcs_p(15, 2)
        self.assertEqual(gcs_p["gcs_p"], 13)
        self.assertEqual(gcs_p["prs"], 2)
        self.assertEqual(gcs_p["prs_description"], "Neither pupil reacts")

    def test_gcs_p_severe_with_no_pupil_response(self):
        """GCS 3 with no pupil response: GCS-P = 3 - 2 = 1."""
        gcs_p = calculate_gcs_p(3, 2)
        self.assertEqual(gcs_p["gcs_p"], 1)

    def test_gcs_p_range_minimum(self):
        """GCS-P minimum is 1 (floor)."""
        gcs_p = calculate_gcs_p(3, 2)
        self.assertEqual(gcs_p["gcs_p"], 1)

    def test_gcs_p_range_maximum(self):
        """GCS-P maximum is 15."""
        gcs_p = calculate_gcs_p(15, 0)
        self.assertEqual(gcs_p["gcs_p"], 15)

    def test_gcs_p_moderate_injury_one_pupil(self):
        """GCS 10, one pupil reacts: GCS-P = 10 - 1 = 9."""
        gcs_p = calculate_gcs_p(10, 1)
        self.assertEqual(gcs_p["gcs_p"], 9)

    def test_gcs_p_invalid_prs(self):
        with self.assertRaises(ValueError):
            calculate_gcs_p(15, 3)

    def test_gcs_p_invalid_gcs(self):
        with self.assertRaises(ValueError):
            calculate_gcs_p(2, 0)

    def test_gcs_p_invalid_gcs_high(self):
        with self.assertRaises(ValueError):
            calculate_gcs_p(16, 0)


class TestPediatricVerbalScale(unittest.TestCase):
    """Test pediatric verbal scale modifications."""

    def test_pediatric_verbal_5(self):
        r = calculate_gcs(4, 5, 6, pediatric=True)
        self.assertEqual(r["verbal_description"], "Coos/babbles (age-appropriate)")
        self.assertTrue(r["pediatric"])

    def test_pediatric_verbal_4(self):
        r = calculate_gcs(4, 4, 6, pediatric=True)
        self.assertEqual(r["verbal_description"], "Irritable crying")

    def test_pediatric_verbal_3(self):
        r = calculate_gcs(4, 3, 6, pediatric=True)
        self.assertEqual(r["verbal_description"], "Cries to pain")

    def test_pediatric_verbal_2(self):
        r = calculate_gcs(4, 2, 6, pediatric=True)
        self.assertEqual(r["verbal_description"], "Moans to pain")

    def test_pediatric_verbal_1(self):
        r = calculate_gcs(4, 1, 6, pediatric=True)
        self.assertEqual(r["verbal_description"], "None")

    def test_pediatric_does_not_affect_total(self):
        adult = calculate_gcs(4, 5, 6, pediatric=False)
        child = calculate_gcs(4, 5, 6, pediatric=True)
        self.assertEqual(adult["total"], child["total"])

    def test_adult_verbal_5_differs_from_pediatric(self):
        adult = calculate_gcs(4, 5, 6, pediatric=False)
        child = calculate_gcs(4, 5, 6, pediatric=True)
        self.assertNotEqual(adult["verbal_description"], child["verbal_description"])


class TestSeverityClassification(unittest.TestCase):
    """Test severity classification function directly."""

    def test_severity_15(self):
        self.assertEqual(classify_severity(15), "Normal")

    def test_severity_14(self):
        self.assertEqual(classify_severity(14), "Mild brain injury")

    def test_severity_13(self):
        self.assertEqual(classify_severity(13), "Mild brain injury")

    def test_severity_12(self):
        self.assertEqual(classify_severity(12), "Moderate brain injury")

    def test_severity_9(self):
        self.assertEqual(classify_severity(9), "Moderate brain injury")

    def test_severity_8(self):
        self.assertEqual(classify_severity(8), "Severe brain injury (coma)")

    def test_severity_3(self):
        self.assertEqual(classify_severity(3), "Severe brain injury (coma)")


class TestInputValidation(unittest.TestCase):
    """Test input validation and error handling."""

    def test_invalid_eye_score_zero(self):
        with self.assertRaises(ValueError):
            calculate_gcs(0, 5, 6)

    def test_invalid_eye_score_five(self):
        with self.assertRaises(ValueError):
            calculate_gcs(5, 5, 6)

    def test_invalid_verbal_score_zero(self):
        with self.assertRaises(ValueError):
            calculate_gcs(4, 0, 6)

    def test_invalid_verbal_score_six(self):
        with self.assertRaises(ValueError):
            calculate_gcs(4, 6, 6)

    def test_invalid_motor_score_zero(self):
        with self.assertRaises(ValueError):
            calculate_gcs(4, 5, 0)

    def test_invalid_motor_score_seven(self):
        with self.assertRaises(ValueError):
            calculate_gcs(4, 5, 7)

    def test_invalid_verbal_string(self):
        with self.assertRaises(ValueError):
            calculate_gcs(4, "abc", 6)

    def test_validate_component_valid(self):
        self.assertEqual(validate_component("eye", 4, EYE_SCORES), 4)

    def test_validate_component_invalid(self):
        with self.assertRaises(ValueError):
            validate_component("eye", 5, EYE_SCORES)


class TestFormatResult(unittest.TestCase):
    """Test result formatting."""

    def test_format_normal(self):
        r = calculate_gcs(4, 5, 6)
        output = format_result(r)
        self.assertIn("Eye (E):    4", output)
        self.assertIn("Verbal (V): 5", output)
        self.assertIn("Motor (M):  6", output)
        self.assertIn("Total GCS:  15", output)
        self.assertIn("Normal", output)

    def test_format_with_gcs_p(self):
        r = calculate_gcs(4, 5, 6)
        gcs_p = calculate_gcs_p(15, 1)
        output = format_result(r, gcs_p)
        self.assertIn("GCS-P:      14", output)
        self.assertIn("PRS=1", output)

    def test_format_intubated(self):
        r = calculate_gcs(3, "1T", 4)
        output = format_result(r)
        self.assertIn("1T", output)
        self.assertIn("intubated", output.lower())

    def test_format_pediatric(self):
        r = calculate_gcs(4, 5, 6, pediatric=True)
        output = format_result(r)
        self.assertIn("Pediatric", output)


class TestCSVBatchProcessing(unittest.TestCase):
    """Test CSV batch processing."""

    def _write_csv(self, rows, fieldnames):
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_batch_basic(self):
        fieldnames = ["patient_id", "eye", "verbal", "motor"]
        rows = [
            {"patient_id": "P001", "eye": "4", "verbal": "5", "motor": "6"},
            {"patient_id": "P002", "eye": "1", "verbal": "1", "motor": "1"},
        ]
        inp = self._write_csv(rows, fieldnames)
        fd, outp = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            results = process_csv(inp, outp)
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]["gcs_total"], 15)
            self.assertEqual(results[0]["severity"], "Normal")
            self.assertEqual(results[1]["gcs_total"], 3)
            self.assertEqual(results[1]["severity"], "Severe brain injury (coma)")
        finally:
            os.unlink(inp)
            os.unlink(outp)

    def test_batch_with_pupils(self):
        fieldnames = ["patient_id", "eye", "verbal", "motor", "pupils"]
        rows = [
            {"patient_id": "P001", "eye": "4", "verbal": "5", "motor": "6", "pupils": "0"},
            {"patient_id": "P002", "eye": "1", "verbal": "1", "motor": "1", "pupils": "2"},
        ]
        inp = self._write_csv(rows, fieldnames)
        fd, outp = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            results = process_csv(inp, outp)
            self.assertEqual(results[0]["gcs_p"], 15)
            self.assertEqual(results[1]["gcs_p"], 1)
        finally:
            os.unlink(inp)
            os.unlink(outp)

    def test_batch_with_intubated(self):
        fieldnames = ["patient_id", "eye", "verbal", "motor", "intubated"]
        rows = [
            {"patient_id": "P001", "eye": "3", "verbal": "1T", "motor": "4", "intubated": "true"},
        ]
        inp = self._write_csv(rows, fieldnames)
        fd, outp = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            results = process_csv(inp, outp)
            self.assertEqual(results[0]["gcs_total"], 8)
            self.assertEqual(results[0]["verbal_display"], "1T")
        finally:
            os.unlink(inp)
            os.unlink(outp)

    def test_batch_with_pediatric(self):
        fieldnames = ["patient_id", "eye", "verbal", "motor", "pediatric"]
        rows = [
            {"patient_id": "P001", "eye": "4", "verbal": "5", "motor": "6", "pediatric": "true"},
        ]
        inp = self._write_csv(rows, fieldnames)
        fd, outp = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            results = process_csv(inp, outp)
            self.assertEqual(results[0]["gcs_total"], 15)
        finally:
            os.unlink(inp)
            os.unlink(outp)

    def test_batch_invalid_data(self):
        fieldnames = ["patient_id", "eye", "verbal", "motor"]
        rows = [
            {"patient_id": "P001", "eye": "99", "verbal": "5", "motor": "6"},
        ]
        inp = self._write_csv(rows, fieldnames)
        fd, outp = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            results = process_csv(inp, outp)
            self.assertIn("ERROR", results[0]["gcs_total"])
        finally:
            os.unlink(inp)
            os.unlink(outp)


class TestCLI(unittest.TestCase):
    """Test CLI argument parsing and execution."""

    def test_cli_score_normal(self):
        """Test: python cli.py score --eye 4 --verbal 5 --motor 6"""
        # Capture stdout
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            rc = cli_main(["score", "--eye", "4", "--verbal", "5", "--motor", "6"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        self.assertEqual(rc, 0)
        self.assertIn("15", output)
        self.assertIn("Normal", output)

    def test_cli_score_intubated(self):
        """Test: python cli.py score --eye 3 --verbal 1T --motor 4 --pupils 1"""
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            rc = cli_main(["score", "--eye", "3", "--verbal", "1T", "--motor", "4", "--pupils", "1"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        self.assertEqual(rc, 0)
        self.assertIn("1T", output)
        self.assertIn("GCS-P", output)

    def test_cli_score_json(self):
        """Test JSON output mode."""
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            rc = cli_main(["score", "--eye", "4", "--verbal", "5", "--motor", "6", "--json"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        self.assertEqual(rc, 0)
        data = json.loads(output)
        self.assertEqual(data["total"], 15)
        self.assertEqual(data["severity"], "Normal")

    def test_cli_score_json_intubated_with_gcs_p(self):
        """Test JSON output with intubated patient and GCS-P."""
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            rc = cli_main(["score", "--eye", "3", "--verbal", "1T", "--motor", "4", "--pupils", "1", "--json"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        self.assertEqual(rc, 0)
        data = json.loads(output)
        self.assertEqual(data["total"], 8)
        self.assertTrue(data["is_intubated"])
        self.assertEqual(data["gcs_p"], 7)

    def test_cli_score_invalid(self):
        """Test CLI with invalid input returns error."""
        from io import StringIO
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            rc = cli_main(["score", "--eye", "99", "--verbal", "5", "--motor", "6"])
            err = sys.stderr.getvalue()
        finally:
            sys.stderr = old_stderr
        self.assertEqual(rc, 1)
        self.assertIn("Error", err)

    def test_cli_batch(self):
        """Test CLI batch processing."""
        # Create temp CSV
        fieldnames = ["patient_id", "eye", "verbal", "motor"]
        rows = [
            {"patient_id": "P001", "eye": "4", "verbal": "5", "motor": "6"},
            {"patient_id": "P002", "eye": "1", "verbal": "1", "motor": "1"},
        ]
        fd_inp, inp_path = tempfile.mkstemp(suffix=".csv")
        os.close(fd_inp)
        fd_out, out_path = tempfile.mkstemp(suffix=".csv")
        os.close(fd_out)

        with open(inp_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            rc = cli_main(["batch", "--input", inp_path, "--output", out_path])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(rc, 0)
        self.assertIn("Processed 2", output)

        # Verify output CSV
        with open(out_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            out_rows = list(reader)
        self.assertEqual(len(out_rows), 2)
        self.assertEqual(out_rows[0]["gcs_total"], "15")
        self.assertEqual(out_rows[1]["gcs_total"], "3")

        os.unlink(inp_path)
        os.unlink(out_path)

    def test_cli_score_pediatric(self):
        """Test CLI with pediatric flag."""
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            rc = cli_main(["score", "--eye", "4", "--verbal", "5", "--motor", "6", "--pediatric"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        self.assertEqual(rc, 0)
        self.assertIn("Pediatric", output)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_all_minimum_scores(self):
        r = calculate_gcs(1, 1, 1)
        self.assertEqual(r["total"], 3)

    def test_all_maximum_scores(self):
        r = calculate_gcs(4, 5, 6)
        self.assertEqual(r["total"], 15)

    def test_verbal_score_as_integer(self):
        r = calculate_gcs(4, 5, 6)
        self.assertEqual(r["verbal"], 5)
        self.assertEqual(r["verbal_display"], "5")

    def test_verbal_score_as_string(self):
        r = calculate_gcs(4, "5", 6)
        self.assertEqual(r["verbal"], 5)
        self.assertEqual(r["verbal_display"], "5")

    def test_gcs_p_with_zero_prs(self):
        gcs_p = calculate_gcs_p(10, 0)
        self.assertEqual(gcs_p["gcs_p"], 10)

    def test_gcs_p_with_max_prs(self):
        gcs_p = calculate_gcs_p(10, 2)
        self.assertEqual(gcs_p["gcs_p"], 8)

    def test_format_result_no_gcs_p(self):
        r = calculate_gcs(4, 5, 6)
        output = format_result(r)
        self.assertNotIn("GCS-P", output)

    def test_format_result_with_gcs_p(self):
        r = calculate_gcs(4, 5, 6)
        gcs_p = calculate_gcs_p(15, 0)
        output = format_result(r, gcs_p)
        self.assertIn("GCS-P:      15", output)


class TestClinicalScenarios(unittest.TestCase):
    """Test realistic clinical scenarios."""

    def test_alert_trauma_patient(self):
        """Alert patient after minor trauma: GCS 15."""
        r = calculate_gcs(4, 5, 6)
        self.assertEqual(r["total"], 15)
        self.assertEqual(r["severity"], "Normal")

    def test_confused_patient(self):
        """Confused patient: E4 V4 M6 = GCS 14."""
        r = calculate_gcs(4, 4, 6)
        self.assertEqual(r["total"], 14)
        self.assertEqual(r["severity"], "Mild brain injury")

    def test_severe_tbi_patient(self):
        """Severe TBI: E1 V1 M2 = GCS 4."""
        r = calculate_gcs(1, 1, 2)
        self.assertEqual(r["total"], 4)
        self.assertEqual(r["severity"], "Severe brain injury (coma)")

    def test_intubated_icu_patient(self):
        """Intubated ICU patient: E3 V1T M4 = GCS 8."""
        r = calculate_gcs(3, "1T", 4)
        self.assertEqual(r["total"], 8)
        self.assertTrue(r["is_intubated"])
        self.assertEqual(r["severity"], "Severe brain injury (coma)")

    def test_postictal_patient(self):
        """Postictal patient: E2 V2 M4 = GCS 8."""
        r = calculate_gcs(2, 2, 4)
        self.assertEqual(r["total"], 8)
        self.assertEqual(r["severity"], "Severe brain injury (coma)")

    def test_decorticate_patient(self):
        """Decorticate posturing: E2 V2 M3 = GCS 7."""
        r = calculate_gcs(2, 2, 3)
        self.assertEqual(r["total"], 7)
        self.assertEqual(r["motor_description"], "Abnormal flexion (decorticate)")

    def test_decerebrate_patient(self):
        """Decerebrate posturing: E1 V1 M2 = GCS 4."""
        r = calculate_gcs(1, 1, 2)
        self.assertEqual(r["total"], 4)
        self.assertEqual(r["motor_description"], "Extension (decerebrate)")

    def test_brain_death_scenario(self):
        """Brain death: GCS 3, no pupil response, GCS-P = 1."""
        r = calculate_gcs(1, 1, 1)
        gcs_p = calculate_gcs_p(r["total"], 2)
        self.assertEqual(r["total"], 3)
        self.assertEqual(gcs_p["gcs_p"], 1)

    def test_pediatric_infant(self):
        """Infant with pediatric scale: E4 V5 M6 = GCS 15."""
        r = calculate_gcs(4, 5, 6, pediatric=True)
        self.assertEqual(r["total"], 15)
        self.assertEqual(r["verbal_description"], "Coos/babbles (age-appropriate)")


if __name__ == "__main__":
    unittest.main()
