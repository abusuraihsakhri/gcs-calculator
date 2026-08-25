# Glasgow Coma Scale (GCS) Calculator

A command-line tool for calculating Glasgow Coma Scale scores, the standard clinical method for assessing consciousness level after brain injury.

## What is GCS?

The Glasgow Coma Scale (Teasdale & Jennett, 1974) is a neurological scale used to objectively assess consciousness. It evaluates three responses:

| Component | Score | Description |
|-----------|-------|-------------|
| **Eye Opening (E)** | 4 | Spontaneous |
| | 3 | To voice/command |
| | 2 | To pressure/pain |
| | 1 | None |
| **Verbal Response (V)** | 5 | Oriented |
| | 4 | Confused conversation |
| | 3 | Inappropriate words |
| | 2 | Incomprehensible sounds |
| | 1 | None |
| **Motor Response (M)** | 6 | Obeys commands |
| | 5 | Localizes pain |
| | 4 | Withdrawal (flexion) |
| | 3 | Abnormal flexion (decorticate) |
| | 2 | Extension (decerebrate) |
| | 1 | None |

**Total GCS = E + V + M** (range 3-15)

### Severity Classification

| GCS Score | Severity |
|-----------|----------|
| 15 | Normal |
| 13-14 | Mild brain injury |
| 9-12 | Moderate brain injury |
| 3-8 | Severe brain injury (coma) |

### GCS-P (GCS-Pupil)

GCS-P adjusts for pupil reactivity: **GCS-P = GCS - Pupil Reactivity Score (PRS)**

| PRS | Meaning |
|-----|---------|
| 0 | Both pupils react |
| 1 | One pupil reacts |
| 2 | Neither pupil reacts |

GCS-P range: 1-15.

### Intubated Patients

For intubated patients, verbal response cannot be assessed. Convention: report verbal as **1T** (e.g., GCS = E3 V1T M4).

### Pediatric Verbal Scale

For children under 2 years or pre-verbal children, use the pediatric verbal scale:

| Score | Description |
|-------|-------------|
| 5 | Coos/babbles (age-appropriate) |
| 4 | Irritable crying |
| 3 | Cries to pain |
| 2 | Moans to pain |
| 1 | None |

## Installation

No dependencies required. Python 3.8+ stdlib only.

```bash
git clone <repo-url>
cd gcs-calculator
```

## Usage

### Single Patient Scoring

```bash
# Normal patient (GCS 15)
python cli.py score --eye 4 --verbal 5 --motor 6

# Severe brain injury (GCS 4)
python cli.py score --eye 1 --verbal 1 --motor 2

# Intubated patient with pupil assessment
python cli.py score --eye 3 --verbal 1T --motor 4 --pupils 1

# Pediatric patient
python cli.py score --eye 4 --verbal 5 --motor 6 --pediatric

# JSON output
python cli.py score --eye 4 --verbal 5 --motor 6 --json
```

### Batch Processing

```bash
python cli.py batch --input patients.csv --output scored.csv
```

Input CSV format:

```csv
patient_id,eye,verbal,motor,pupils,intubated,pediatric
P001,4,5,6,0,false,false
P002,3,1T,4,0,true,false
P003,1,1,1,2,false,false
```

Output adds columns: `gcs_total`, `severity`, `verbal_display`, and optionally `gcs_p`, `prs_description`.

### Python API

```python
from gcs import calculate_gcs, calculate_gcs_p

# Calculate GCS
result = calculate_gcs(eye=4, verbal=5, motor=6)
print(result["total"])       # 15
print(result["severity"])    # "Normal"

# Calculate GCS-P
gcs_p = calculate_gcs_p(gcs_total=15, pupil_reactivity_score=0)
print(gcs_p["gcs_p"])       # 15

# Intubated patient
result = calculate_gcs(eye=3, verbal="1T", motor=4)
print(result["total"])       # 8
print(result["is_intubated"]) # True
```

## Running Tests

```bash
python -m pytest test_gcs.py -v
```

Or with unittest:

```bash
python -m unittest test_gcs.py -v
```

## Project Structure

```
gcs-calculator/
  gcs.py          # Core GCS scoring logic and CLI
  cli.py          # CLI entry point (thin wrapper)
  test_gcs.py     # Comprehensive test suite
  sample.csv      # Example batch input
  README.md       # This file
```

## Clinical Disclaimer

This tool is for educational and reference purposes only. It is not a substitute for professional clinical judgment. Always consult qualified medical professionals for patient assessment and treatment decisions.

## References

- Teasdale, G., & Jennett, B. (1974). Assessment of coma and impaired consciousness: a practical scale. *The Lancet*, 304(7872), 81-84.
- Teasdale, G., et al. (2014). A new assessment of the Glasgow Coma Scale. *Journal of Neurotrauma*, 31(1), 34-37.

## License

MIT License. See [LICENSE](LICENSE).
