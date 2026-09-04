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
Total GCS = Eye (E) + Verbal (V) + Motor (M)
GCS Range: 3 (deep coma) to 15 (normal)

GCS-P = GCS_total - Pupil Reactivity Score (PRS)
GCS-P Range: 1 to 15

Severity Classification:
  15      : Normal
  13-14   : Mild brain injury
  9-12    : Moderate brain injury
  3-8     : Severe brain injury (coma)
```

---

## 💻 CLI Quickstart & Usage

### Installation
```bash
pip install -r requirements.txt
```

### 1. Score a Single Patient
```bash
python cli.py score --eye 4 --verbal 5 --motor 6
python cli.py score --eye 3 --verbal 1T --motor 4 --pupils 1
python cli.py score --eye 2 --verbal 2 --motor 3 --pediatric --json
```

### 2. Batch Process from CSV
```bash
python cli.py batch --input patients.csv --output scored.csv
```

### 3. Run Distributed Component Audit
```bash
python cli.py audit --task-id TASK-001 --primary 12.5 --secondary 4.0
```

### 4. Query Supervisory Assistant
```bash
python cli.py chat "Explain GCS scoring criteria"
```

### 5. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 6. Start REST API Server
```bash
python cli.py serve --host 0.0.0.0 --port 8000
```

### Parameter Reference
- `--eye`: Eye Opening score (1-4)
- `--verbal`: Verbal Response score (1-5 or 1T for intubated)
- `--motor`: Motor Response score (1-6)
- `--pupils`: Pupil Reactivity Score (0-2) for GCS-P
- `--intubated`: Flag for intubated patients
- `--pediatric`: Use pediatric verbal scale
- `--json`: Output result as JSON

### Input Data Schema (CSV)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `patient_id` | Patient identifier | Optional |
| `eye` | Eye Opening score (1-4) | Required |
| `verbal` | Verbal Response score (1-5 or 1T) | Required |
| `motor` | Motor Response score (1-6) | Required |
| `pupils` | Pupil Reactivity Score (0-2) | Optional |
| `intubated` | Intubated flag (true/false) | Optional |
| `pediatric` | Pediatric scale flag (true/false) | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).
* **Multi-Agent Supervisory System:** Distributed component workers for QC, safety, and protocol conformance.

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Run specific test files:

```bash
pytest test_gcs.py -v          # Core GCS functionality (102 tests)
pytest tests/ -v               # Enterprise module tests
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t gcs-calculator .
docker run -p 8000:8000 gcs-calculator
```

---

## 📁 Project Structure

```
gcs-calculator/
├── gcs.py                 # Core GCS calculator logic and CLI
├── cli.py                 # CLI entry point
├── test_gcs.py            # Core functionality tests
├── enrichment.py          # Clinical enrichment engines
├── simulator.py           # Simulation benchmark tool
├── agents/                # Enterprise multi-agent module
│   ├── api.py             # FastAPI REST server
│   ├── base.py            # Security, PHI guard, audit trail
│   ├── models.py          # Pydantic data models
│   ├── supervisor.py      # Multi-agent orchestrator
│   ├── workers.py         # Specialized worker agents
│   ├── llm_factory.py     # LLM provider factory
│   ├── metrics.py         # Prometheus metrics exporter
│   ├── streamer.py        # WebSocket telemetry streamer
│   └── learning.py        # Bayesian calibration engine
├── tests/                 # Enterprise module tests
│   ├── test_gcs_calculator.py
│   └── test_enrichment.py
├── web/                   # Operations console (HTML)
├── sample.csv             # Sample patient data
├── benchmark_dataset.json # Benchmark test cases
├── Dockerfile             # Container definition
├── docker-compose.yml     # Docker Compose configuration
└── requirements.txt       # Python dependencies
```
