"""Classe de base abstraite pour les scrapers."""

from abc import ABC, abstractmethod
from typing import Dict, Iterator, Optional

from loguru import logger

from app.models import JobOffer, SearchCriteria


class BaseScraper(ABC):
    """Classe de base pour tous les scrapers d'offres d'emploi."""

    name: str = "base"
    base_url: str = ""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        logger.info(f"Scraper {self.name} initialisé")

    @abstractmethod
    def search(self, criteria: SearchCriteria) -> Iterator[JobOffer]:
        """Recherche des offres selon les critères donnés."""

    @abstractmethod
    def get_job_details(self, job_id: str) -> Optional[JobOffer]:
        """Récupère les détails complets d'une offre."""

    def close(self) -> None:
        """Ferme les ressources du scraper."""
        logger.info(f"Scraper {self.name} fermé")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
