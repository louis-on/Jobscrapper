# JobScraper Web

Version web de JobScraper, construite avec FastAPI. Source des offres : API Adzuna (agrège Indeed, Monster, etc.).

## Lancer en local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis renseigner ADZUNA_APP_ID et ADZUNA_APP_KEY
uvicorn app.api:app --reload
```

Puis ouvrir http://127.0.0.1:8000/docs.

## Endpoints

- `GET /health`
- `GET /jobs?limit=50`
- `POST /collect?keywords=python&location=Paris&max_results=50`

## Configuration

- `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` : clés API Adzuna.
- `JOBSCRAPER_DB_PATH` : chemin de la base SQLite (défaut `data/jobs.db`).

## État

La collecte est branchée sur Adzuna. Les autres sources du projet d'origine (LinkedIn, HelloWork, France Travail, WTTJ) ne sont pas encore portées.
