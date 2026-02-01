## FastAPI backend (boilerplate)

### Requirements

- Python 3.11+ recommended

### Setup

From the repo root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
```

### Run (dev)

```bash
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

Then open:

- `http://localhost:8000/health`
- `http://localhost:8000/docs`

### Environment variables

Copy `backend\.env.example` to `backend\.env` and adjust as needed.
