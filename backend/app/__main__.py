from app.main import app

if __name__ == "__main__":
    # Allows: `python -m app` (useful for some debuggers),
    # but for dev you probably want:
    # uvicorn app.main:app --reload --app-dir backend
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
