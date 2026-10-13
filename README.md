# Glasgow Coma Scale (GCS) Calculator

A Glasgow Coma Scale scoring tool with a standalone browser interface, Python CLI, CSV processing, optional pupil reactivity scoring (GCS-P), and a FastAPI backend.

## Use the calculator

Open `web/index.html` in a browser. The primary calculator works without a server, account, build step, external dependencies or network access. Select the eye (E), verbal (V), and motor (M) responses; the total (3–15) updates immediately. You can optionally enter pupil reactivity (PRS: 0–2) to obtain GCS-P, or choose preverbal pediatric verbal descriptions.

**Important:** If the verbal response cannot be assessed, including because of intubation, mark it **NT (not testable)**. In that case neither a total GCS nor GCS-P is reported; only the assessable components are displayed. The legacy CLI input `1T` is still accepted but now means V-NT, not a numeric V1.

The TBI severity bands are **mild: 13–15**, **moderate: 9–12**, **severe: 3–8**. These describe the score range in traumatic brain injury and do not independently establish a diagnosis, prognosis or management plan. GCS 15 alone does not establish that a person is neurologically normal.

Clinical references:
- [Glasgow Coma Scale official FAQ](https://www.glasgowcomascale.org/faq/) — component scoring and NT rules
- [NICE NG232: Head injury](https://www.nice.org.uk/guidance/ng232/chapter/recommendations) — document E, V and M separately

## Python usage

The core scorer (`gcs.py`) uses the Python standard library. Python 3.10+ is supported; optional API and test dependencies are in `requirements.txt`.

```bash
python cli.py score --eye 4 --verbal 5 --motor 6
python cli.py score --eye 3 --verbal NT --motor 4
python cli.py score --eye 2 --verbal 3 --motor 4 --pupils 1 --json
python cli.py batch --input sample.csv --output scored.csv
```

The CSV schema requires `eye`, `verbal`, and `motor`. Optional columns include `pupils`, `intubated`, `pediatric`, and `patient_id`. The output includes the component notation, severity where classifiable, and GCS-P when available. Invalid rows are indicated with an error instead of silently substituting missing components.

Do not add identifiable patient information to clinical examples or shared output files.

## Optional server and supervisory tools

```bash
python -m pip install -r requirements.txt
python cli.py serve --host 127.0.0.1 --port 8000
```

The calculator is then available at `http://127.0.0.1:8000/`. The API schema is at `/docs`, health at `/health`, JSON counters at `/metrics`, and the optional backend supervisory audit at `/api/audit`. The advanced audit panel on the web page only works when served from this backend; **the browser-only GitHub Pages application does not run the Python server or supervisory audit**.

Other CLI subcommands are `audit`, `chat`, and `verify-audit`. These operate through an auxiliary mocked supervisory module; they are not part of the clinical GCS scoring algorithm and should not be treated as validated medical decision support. The REST endpoints have **no authentication** and must not be exposed directly to the public internet without an appropriate access-control layer.

Docker Compose runs the backend on localhost by default. Set a private secret in the environment before starting it (see `.env.example`):

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

For audit HMACs, set the `AUDIT_SECRET_KEY` environment variable to a confidential random key in long-lived deployments. Without this setting, an unpredictable session-only key is generated. Audit records are held in process memory, not a durable independent audit log; they should not be used for compliance-grade logging.

## Development and verification

```bash
python -m pip install -r requirements.txt
python -m compileall -q .
python -m pytest -q
```

The CI workflow tests Python 3.10, 3.11 and 3.12 and validates inline browser JavaScript syntax. `web/index.html` requires no npm package installation, Pyodide, or JavaScript build step. A GitHub Actions Pages workflow packages the `web/` directory; publication also requires Pages to be enabled for the repository.

The app uses standard HTML/CSS/JavaScript and Python with FastAPI/Pydantic for optional server workflows. Browser calculations operate in memory only; they do not use browser storage or transmit clinical selections. The advanced audit panel makes a same-origin request only after its button is pressed.

## License

[MIT](LICENSE).
