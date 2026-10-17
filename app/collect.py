"""Collecte des offres via les scrapers existants et stockage."""

from typing import List, Optional

from app.storage import save_jobs


def collect_jobs(keywords: List[str], location: Optional[str], max_results: int) -> int:
    """
    Lance la recherche et enregistre les offres.

    Le branchement sur les scrapers du projet d'origine (jobscraper.scrapers)
    reste à faire : cette fonction ne retourne pour l'instant aucune offre.
    """
    jobs: list = []
    return save_jobs(jobs)
