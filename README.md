# GCS Calculator

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Glasgow Coma Scale (GCS) Calculator.

Implements the standard GCS scoring system (Teasdale & Jennett, 1974) with:
- Eye Opening (E): 1-4
- Verbal Response (V): 1-5 (or 1T for intubated patients)
- Motor Response (M): 1-6
- Total GCS = E + V + M (range 3-15)
- GCS-P (GCS-Pupil) score: GCS minus Pupil Reactivity Score
- Pediatric verbal scale modifications

Stdlib only. No external dependencies.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`parse_verbal_score()`**: Parse a verbal score that may be an int or a string like '1T'.

Returns (numeric_score, is_intubated).
The 'T' suffix indicates the patient is intubated and verbal response
cannot be assessed; the numeric part is reported as 1T by convention.
- **`validate_component()`**: Validate a GCS component score and return its integer value.
- **`classify_severity()`**: Return severity classification string for a GCS total score.
- **`calculate_gcs()`**: Calculate Glasgow Coma Scale score.

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
    When intubated, verbal is reported as 1T and excluded from total.
pediatric : bool
    If True, use pediatric verbal scale descriptions.

Returns
-------
dict with keys:
    eye: int
    eye_description: str
    verbal: int
    verbal_description: str
    verbal_display: str  (e.g. "3" or "1T")
    motor: int
    motor_description: str
    total: int
    severity: str
    is_intubated: bool
    pediatric: bool
- **`calculate_gcs_p()`**: Calculate GCS-P (GCS-Pupil) score.

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

---

## 📐 Mathematical Formulation & Logic

```text
  """Calculate Glasgow Coma Scale score.
  """Calculate GCS-P (GCS-Pupil) score.
  result = calculate_gcs(
  gcs_p = calculate_gcs_p(result["total"], pupils_val)
  help="Calculate GCS for a single patient",
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --eye <value> --verbal <value> --motor <value> --pupils <value>
```

### Parameter Reference
- `--eye`: Specifies input measurement or parameter value.
- `--verbal`: Specifies input measurement or parameter value.
- `--motor`: Specifies input measurement or parameter value.
- `--pupils`: Specifies input measurement or parameter value.
- `--pediatric`: Specifies input measurement or parameter value.
- `--json`: Specifies input measurement or parameter value.
- `--input`: Specifies input measurement or parameter value.
- `--output`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `patient_id` | Parameter / observation metric | Required |
| `eye` | Parameter / observation metric | Required |
| `verbal` | Parameter / observation metric | Required |
| `motor` | Parameter / observation metric | Required |
| `pupils` | Parameter / observation metric | Required |
| `intubated` | Parameter / observation metric | Required |
| `pediatric` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t gcs-calculator .
docker run -p 8000:8000 gcs-calculator
```
