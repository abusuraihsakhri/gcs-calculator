#!/usr/bin/env python3
"""
Glasgow Coma Scale (GCS) Calculator.

Implements the standard GCS scoring system (Teasdale & Jennett, 1974) with:
- Eye Opening (E): 1-4
- Verbal Response (V): 1-5 (or 1T for intubated patients)
- Motor Response (M): 1-6
- Total GCS = E + V + M (range 3-15)
- GCS-P (GCS-Pupil) score: GCS minus Pupil Reactivity Score
- Pediatric verbal scale modifications

Stdlib only. No external dependencies.
"""

import argparse
import csv
import json
import sys

# ---------------------------------------------------------------------------
# Component score definitions
# ---------------------------------------------------------------------------

EYE_SCORES = {
    4: "Spontaneous",
    3: "To voice/command",
    2: "To pressure/pain",
    1: "None",
}

VERBAL_SCORES = {
    5: "Oriented",
    4: "Confused conversation",
    3: "Inappropriate words",
    2: "Incomprehensible sounds",
    1: "None",
}

MOTOR_SCORES = {
    6: "Obeys commands",
    5: "Localizes pain",
    4: "Withdrawal (flexion)",
    3: "Abnormal flexion (decorticate)",
    2: "Extension (decerebrate)",
    1: "None",
}

# Pediatric verbal scale (for children < 2 years or pre-verbal)
PEDIATRIC_VERBAL_SCORES = {
    5: "Coos/babbles (age-appropriate)",
    4: "Irritable crying",
    3: "Cries to pain",
    2: "Moans to pain",
    1: "None",
}

# Severity classification thresholds
SEVERITY_MAP = [
    (13, "Mild TBI score range (13-15)"),
    (9, "Moderate TBI score range (9-12)"),
    (3, "Severe TBI score range (3-8)"),
]

# Pupil Reactivity Score labels
PRS_LABELS = {
    0: "Both pupils react",
    1: "One pupil reacts",
    2: "Neither pupil reacts",
}


# ---------------------------------------------------------------------------
# Core scoring functions
# ---------------------------------------------------------------------------

def parse_verbal_score(value):
    """Parse a verbal score that may be an int or a string like '1T'.

    Returns (numeric_score, is_intubated).
    The 'T' suffix indicates the patient is intubated and verbal response
    cannot be assessed; the numeric part is reported as 1T by convention.
    """
    s = str(value).strip().upper()
    if s == "NT":
        return None, True
    is_intubated = False
    if s.endswith("T"):
        is_intubated = True
        s = s[:-1]
    try:
        num = int(s)
    except ValueError:
        raise ValueError(
            f"Invalid verbal score: '{value}'. "
            f"Expected 1-5 or 1T-5T for intubated patients."
        )
    return num, is_intubated


def validate_component(name, value, valid_scores):
    """Validate a GCS component score and return its integer value."""
    if isinstance(value, bool) or not (
        isinstance(value, int) or
        (isinstance(value, str) and value.strip().isascii() and value.strip().isdigit())
    ):
        raise ValueError(f"Invalid {name} score: '{value}'. Must be an integer.")
    num = int(value)
    if num not in valid_scores:
        low = min(valid_scores)
        high = max(valid_scores)
        raise ValueError(
            f"Invalid {name} score: {num}. Must be between {low} and {high}."
        )
    return num


def classify_severity(gcs_total):
    """Return a TBI-associated score range, not a clinical diagnosis."""
    if isinstance(gcs_total, bool) or not isinstance(gcs_total, int) or not 3 <= gcs_total <= 15:
        raise ValueError("GCS total must be an integer from 3 to 15.")
    for threshold, label in SEVERITY_MAP:
        if gcs_total >= threshold:
            return label
    raise AssertionError("Unreachable GCS severity range")


def calculate_gcs(eye, verbal, motor, intubated=False, pediatric=False):
    """Calculate Glasgow Coma Scale score.

    Parameters
    ----------
    eye : int
        Eye Opening score (1-4).
    verbal : int or str
        Verbal Response score (1-5). Use '1T' etc. for intubated patients.
    motor : int
        Motor Response score (1-6).
    intubated : bool
        If True and verbal is not explicitly 'T'-suffixed, mark as intubated.
        When intubated, verbal is not testable (NT); no total is reported.
    pediatric : bool
        If True, use pediatric verbal scale descriptions.

    Returns
    -------
    dict with keys:
        eye: int
        eye_description: str
        verbal: int or None (not testable)
        verbal_description: str
        verbal_display: str  (e.g. "3" or "1T")
        motor: int
        motor_description: str
        total: int or None
        severity: str
        is_intubated: bool
        pediatric: bool
    """
    # Validate components
    e = validate_component("eye", eye, EYE_SCORES)
    m = validate_component("motor", motor, MOTOR_SCORES)

    # Parse verbal (may include T suffix)
    v, verbal_intubated = parse_verbal_score(verbal)
    is_intubated = intubated or verbal_intubated

    if v is not None and v not in VERBAL_SCORES:
        raise ValueError(
            f"Invalid verbal score: {v}. Must be between 1 and 5."
        )

    # An untestable verbal component must not be imputed as 1.
    # Retain E and M, but withhold the total, severity and GCS-P.
    verbal_desc_map = PEDIATRIC_VERBAL_SCORES if pediatric else VERBAL_SCORES
    verbal_display = "NT" if is_intubated else str(v)
    verbal_description = "Not testable (intubated)" if is_intubated else verbal_desc_map[v]
    total = None if is_intubated else e + v + m

    return {
        "eye": e,
        "eye_description": EYE_SCORES[e],
        "verbal": None if is_intubated else v,
        "verbal_description": verbal_description,
        "verbal_display": verbal_display,
        "motor": m,
        "motor_description": MOTOR_SCORES[m],
        "total": total,
        "severity": None if total is None else classify_severity(total),
        "is_intubated": is_intubated,
        "pediatric": pediatric,
    }


def calculate_gcs_p(gcs_total, pupil_reactivity_score):
    """Calculate GCS-P (GCS-Pupil) score.

    Parameters
    ----------
    gcs_total : int
        Total GCS score (3-15).
    pupil_reactivity_score : int
        Pupil Reactivity Score (PRS): 0, 1, or 2.
        0 = Both pupils react
        1 = One pupil reacts
        2 = Neither pupil reacts

    Returns
    -------
    dict with keys:
        gcs: int
        prs: int
        prs_description: str
        gcs_p: int  (range 1-15)
    """
    if (isinstance(gcs_total, bool) or not isinstance(gcs_total, int)
            or not 3 <= gcs_total <= 15):
        raise ValueError(f"GCS total must be an integer from 3 to 15, got {gcs_total}.")
    if isinstance(pupil_reactivity_score, bool) or not (
        isinstance(pupil_reactivity_score, int) or
        (isinstance(pupil_reactivity_score, str)
         and pupil_reactivity_score.strip().isascii()
         and pupil_reactivity_score.strip().isdigit())
    ):
        raise ValueError("PRS must be an integer from 0 to 2.")
    prs = int(pupil_reactivity_score)
    if prs not in PRS_LABELS:
        raise ValueError(f"PRS must be 0, 1, or 2. Got {prs}.")
    gcs_p = gcs_total - prs
    # GCS-P floor is 1 (GCS 3 - PRS 2 = 1)
    if gcs_p < 1:
        gcs_p = 1
    return {
        "gcs": gcs_total,
        "prs": prs,
        "prs_description": PRS_LABELS[prs],
        "gcs_p": gcs_p,
    }


def format_result(result, gcs_p_result=None):
    """Format a GCS result dict into a human-readable string."""
    lines = []
    lines.append(f"Eye (E):    {result['eye']} - {result['eye_description']}")
    lines.append(f"Verbal (V): {result['verbal_display']} - {result['verbal_description']}")
    lines.append(f"Motor (M):  {result['motor']} - {result['motor_description']}")
    lines.append(f"Total GCS:  {result['total'] if result['total'] is not None else 'Not available (V-NT)'}")
    lines.append(f"Severity:   {result['severity'] if result['severity'] is not None else 'Not classifiable'}")
    if result["is_intubated"]:
        lines.append("Note:       Verbal response is not testable; no valid total GCS or GCS-P.")
    if result["pediatric"]:
        lines.append("Scale:      Pediatric verbal scale")
    if gcs_p_result:
        lines.append(f"GCS-P:      {gcs_p_result['gcs_p']} (PRS={gcs_p_result['prs']}: {gcs_p_result['prs_description']})")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CSV batch processing
# ---------------------------------------------------------------------------

def process_csv(input_path, output_path):
    """Process a CSV file of patients and compute GCS scores.

    Expected CSV columns: patient_id (optional), eye, verbal, motor,
    and optionally: pupils (PRS), intubated, pediatric.

    Output adds columns: gcs_total, severity, verbal_display, gcs_p (if pupils given).
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        required = {"eye", "verbal", "motor"}
        if not required.issubset({k.strip().lower() for k in fieldnames}):
            raise ValueError("CSV requires eye, verbal, and motor columns.")
        rows = list(reader)
        if any(None in row for row in rows):
            raise ValueError("CSV row contains more fields than the header.")

    # Build output fieldnames
    extra_fields = ["gcs_total", "severity", "verbal_display"]
    # Check if any row has a 'pupils' column
    has_pupils_col = any(k.strip().lower() == "pupils" for k in fieldnames)

    if has_pupils_col:
        extra_fields.extend(["gcs_p", "prs_description"])

    out_fieldnames = fieldnames + [name for name in extra_fields if name not in fieldnames]
    out_rows = []

    for row in rows:
        # Extract values with flexible column name matching
        def get_val(key, default=None):
            for k, v in row.items():
                if k is not None and k.strip().lower() == key.lower():
                    return v
            return default

        eye_val = get_val("eye", 1)
        verbal_val = get_val("verbal", 1)
        motor_val = get_val("motor", 1)
        intubated_val = str(get_val("intubated", "false")).lower() in ("true", "1", "yes")
        pediatric_val = str(get_val("pediatric", "false")).lower() in ("true", "1", "yes")
        pupils_val = get_val("pupils")

        try:
            result = calculate_gcs(
                eye=eye_val,
                verbal=verbal_val,
                motor=motor_val,
                intubated=intubated_val,
                pediatric=pediatric_val,
            )
            merged = dict(row)
            merged["gcs_total"] = result["total"] if result["total"] is not None else ""
            merged["severity"] = result["severity"] or "Not classifiable (V-NT)"
            merged["verbal_display"] = result["verbal_display"]

            if has_pupils_col and pupils_val is not None and str(pupils_val).strip():
                if result["total"] is not None:
                    gcs_p = calculate_gcs_p(result["total"], pupils_val)
                    merged["gcs_p"] = gcs_p["gcs_p"]
                    merged["prs_description"] = gcs_p["prs_description"]

        except ValueError as e:
            merged = dict(row)
            merged["gcs_total"] = f"ERROR: {e}"
            merged["severity"] = "ERROR"
            merged["verbal_display"] = "ERROR"

        out_rows.append(merged)

    # Prevent spreadsheet formula execution when users open the CSV in Excel
    # or similar applications. Keep the returned Python row data unchanged.
    def safe_csv_value(value):
        if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + value
        return value

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        for row in out_rows:
            writer.writerow({key: safe_csv_value(value) for key, value in row.items()})

    return out_rows


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    """Build the argument parser for the CLI."""
    p = argparse.ArgumentParser(
        prog="gcs",
        description="Glasgow Coma Scale (GCS) Calculator",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # --- score subcommand ---
    s = sub.add_parser(
        "score",
        help="Calculate GCS for a single patient",
    )
    s.add_argument(
        "--eye", "-e", type=int, required=True,
        help="Eye Opening score (1-4): 4=Spontaneous, 3=To voice, 2=To pain, 1=None",
    )
    s.add_argument(
        "--verbal", "-v", type=str, required=True,
        help="Verbal Response score (1-5; NT or legacy 1T if intubated): "
             "5=Oriented, 4=Confused, 3=Inappropriate words, 2=Incomprehensible, 1=None",
    )
    s.add_argument(
        "--motor", "-m", type=int, required=True,
        help="Motor Response score (1-6): 6=Obeys, 5=Localizes, 4=Withdrawal, "
             "3=Abnormal flexion, 2=Extension, 1=None",
    )
    s.add_argument(
        "--pupils", "-p", type=int, default=None,
        help="Pupil Reactivity Score (0-2) for GCS-P calculation: "
             "0=Both react, 1=One reacts, 2=Neither reacts",
    )
    s.add_argument(
        "--intubated", action="store_true",
        help="Patient is intubated (verbal response NT; no total GCS)",
    )
    s.add_argument(
        "--pediatric", action="store_true",
        help="Use pediatric verbal scale (for children < 2 years)",
    )
    s.add_argument(
        "--json", action="store_true",
        help="Output result as JSON",
    )

    # --- batch subcommand ---
    b = sub.add_parser(
        "batch",
        help="Batch process patients from a CSV file",
    )
    b.add_argument(
        "--input", "-i", required=True,
        help="Input CSV file path (columns: eye, verbal, motor, [pupils, intubated, pediatric])",
    )
    b.add_argument(
        "--output", "-o", required=True,
        help="Output CSV file path",
    )

    # --- audit subcommand ---
    a = sub.add_parser(
        "audit",
        help="Run a distributed component audit task through the supervisor",
    )
    a.add_argument(
        "--task-id", required=True,
        help="Unique task identifier for the audit",
    )
    a.add_argument(
        "--target", default="CLI-TARGET",
        help="Target identifier for the audit",
    )
    a.add_argument(
        "--primary", type=float, default=10.0,
        help="Primary metric value",
    )
    a.add_argument(
        "--secondary", type=float, default=5.0,
        help="Secondary metric value",
    )
    a.add_argument(
        "--status", default="NOMINAL",
        help="Status descriptor (NOMINAL, DISCORDANT_ANOMALY, etc.)",
    )
    a.add_argument(
        "--critical", action="store_true",
        help="Flag as critical task",
    )

    # --- chat subcommand ---
    c = sub.add_parser(
        "chat",
        help="Query the air-gapped supervisory assistant",
    )
    c.add_argument(
        "query",
        nargs="+",
        help="Query text for the supervisory assistant",
    )

    # --- verify-audit subcommand ---
    v = sub.add_parser(
        "verify-audit",
        help="Verify the HMAC-SHA256 audit trail integrity",
    )

    # --- serve subcommand ---
    sv = sub.add_parser(
        "serve",
        help="Start the FastAPI REST server",
    )
    sv.add_argument(
        "--host", default="0.0.0.0",
        help="Host to bind the server to",
    )
    sv.add_argument(
        "--port", type=int, default=8000,
        help="Port to bind the server to",
    )

    return p


def main(argv=None):
    """CLI entry point."""
    p = build_parser()
    a = p.parse_args(argv)

    if a.cmd == "score":
        try:
            result = calculate_gcs(
                eye=a.eye,
                verbal=a.verbal,
                motor=a.motor,
                intubated=a.intubated,
                pediatric=a.pediatric,
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        gcs_p_result = None
        if a.pupils is not None:
            if result["total"] is None:
                print("Error: GCS-P cannot be calculated with a not-testable verbal response.", file=sys.stderr)
                return 1
            try:
                gcs_p_result = calculate_gcs_p(result["total"], a.pupils)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1

        if a.json:
            output = {
                "eye": result["eye"],
                "eye_description": result["eye_description"],
                "verbal": result["verbal"],
                "verbal_description": result["verbal_description"],
                "verbal_display": result["verbal_display"],
                "motor": result["motor"],
                "motor_description": result["motor_description"],
                "total": result["total"],
                "severity": result["severity"],
                "is_intubated": result["is_intubated"],
                "pediatric": result["pediatric"],
            }
            if gcs_p_result:
                output["gcs_p"] = gcs_p_result["gcs_p"]
                output["prs"] = gcs_p_result["prs"]
                output["prs_description"] = gcs_p_result["prs_description"]
            print(json.dumps(output, indent=2))
        else:
            print(format_result(result, gcs_p_result))

        return 0

    if a.cmd == "batch":
        try:
            results = process_csv(a.input, a.output)
            print(f"Processed {len(results)} patients -> {a.output}")
        except FileNotFoundError:
            print(f"Error: Input file not found: {a.input}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    if a.cmd == "audit":
        try:
            from agents.supervisor import SystemSupervisor
            from agents.models import SystemTaskPayload
            supervisor = SystemSupervisor(model_provider="mock")
            payload = SystemTaskPayload(
                task_id=a.task_id,
                target_identifier=a.target,
                primary_metric=a.primary,
                secondary_metric=a.secondary,
                status_descriptor=a.status,
                is_critical_flag=a.critical,
            )
            dossier = supervisor.process_task(payload)
            print(json.dumps(dossier.to_dict(), indent=2, default=str))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    if a.cmd == "chat":
        try:
            from agents.supervisor import SystemSupervisor
            supervisor = SystemSupervisor(model_provider="mock")
            query = " ".join(a.query)
            response = supervisor.query_supervisory_chat(query)
            print(response)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    if a.cmd == "verify-audit":
        try:
            from agents.base import AuditLogger
            verified = AuditLogger.verify_integrity()
            trail = AuditLogger.get_trail()
            print(f"Audit trail entries: {len(trail)}")
            print(f"Integrity verified: {verified}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    if a.cmd == "serve":
        try:
            import uvicorn
            from agents.api import app
            uvicorn.run(app, host=a.host, port=a.port)
        except ImportError:
            print("Error: uvicorn and fastapi are required for the server.", file=sys.stderr)
            print("Install with: pip install fastapi uvicorn", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
