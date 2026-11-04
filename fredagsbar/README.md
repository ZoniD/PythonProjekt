# Fredagsbarens event-system

Flask API (`api.py`) + Streamlit-frontend (`app.py`), der taler sammen via `httpx`.

## Kør med Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:8501
- API: http://localhost:5000 (fx `GET http://localhost:5000/events` i Postman)

## Kør lokalt uden Docker

```bash
uv sync
uv run api.py                 # terminal 1: API'en på port 5000
uv run streamlit run app.py   # terminal 2: frontenden på port 8501
```

## Dokumentation

`swagger.json` beskriver alle seks endpoints. Den kan åbnes i [Swagger Editor](https://editor.swagger.io).
