"""API web minimale pour JobScraper."""

from typing import List, Optional

from fastapi import FastAPI, Query

from app.collect import collect_jobs
from app.storage import list_jobs

app = FastAPI(title="JobScraper Web")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/jobs")
def get_jobs(limit: int = Query(50, ge=1, le=500)) -> List[dict]:
    return list_jobs(limit=limit)


@app.post("/collect")
def post_collect(
    keywords: List[str] = Query(...),
    location: Optional[str] = None,
    max_results: int = Query(50, ge=1, le=500),
) -> dict:
    count = collect_jobs(keywords=keywords, location=location, max_results=max_results)
    return {"collected": count}
