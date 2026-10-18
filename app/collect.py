"""Collecte des offres via Adzuna et stockage."""

from typing import List, Optional

from dotenv import load_dotenv

from app.models import SearchCriteria
from app.scrapers.adzuna import AdzunaScraper
from app.storage import save_jobs

load_dotenv()


def collect_jobs(keywords: List[str], location: Optional[str], max_results: int) -> int:
    """Lance la recherche Adzuna et enregistre les offres. Retourne le nombre sauvegardé."""
    criteria = SearchCriteria(
        keywords=keywords,
        location=location or "France",
        max_results=max_results,
    )
    with AdzunaScraper() as scraper:
        jobs = list(scraper.search(criteria))
    return save_jobs(jobs)
