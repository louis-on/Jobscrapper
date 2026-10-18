"""Stockage simple des offres dans SQLite."""

import json
import os
import sqlite3
from pathlib import Path
from typing import Iterable, List


def _db_path() -> Path:
    return Path(os.getenv("JOBSCRAPER_DB_PATH", "data/jobs.db"))


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, source TEXT, data TEXT)"
    )
    return conn


def save_jobs(jobs: Iterable) -> int:
    """Enregistre les offres (objets pydantic ou dicts). Retourne le nombre inséré."""
    conn = _connect()
    count = 0
    for job in jobs:
        data = job.model_dump(mode="json") if hasattr(job, "model_dump") else dict(job)
        conn.execute(
            "INSERT OR REPLACE INTO jobs (id, source, data) VALUES (?, ?, ?)",
            (str(data.get("id")), data.get("source", ""), json.dumps(data, ensure_ascii=False)),
        )
        count += 1
    conn.commit()
    conn.close()
    return count


def list_jobs(limit: int = 50) -> List[dict]:
    conn = _connect()
    rows = conn.execute("SELECT data FROM jobs LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]
