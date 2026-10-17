# JobScraper Web

Version web minimale de JobScraper, construite avec FastAPI.

## Lancer en local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api:app --reload
```

Puis ouvrir http://127.0.0.1:8000/docs.

## Endpoints

- `GET /health`
- `GET /jobs?limit=50`
- `POST /collect?keywords=python&location=Paris&max_results=50`

## État

La collecte n'est pas encore branchée sur les scrapers du projet d'origine.
