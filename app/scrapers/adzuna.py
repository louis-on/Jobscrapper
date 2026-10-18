"""Scraper pour l'API Adzuna (agrégateur: Indeed, Monster, etc.)."""

import os
from datetime import datetime
from typing import Dict, Iterator, Optional, Tuple

import requests
from loguru import logger

from app.models import (
    ContractType,
    DatePosted,
    JobOffer,
    SearchCriteria,
    SortBy,
)
from app.scrapers.base import BaseScraper


class AdzunaScraper(BaseScraper):
    """
    Client de l'API Adzuna.

    Clés gratuites: https://developer.adzuna.com/
    """

    name = "adzuna"
    base_url = "https://api.adzuna.com/v1/api/jobs"

    CONTRACT_MAPPING = {
        ContractType.CDI: "permanent",
        ContractType.CDD: "contract",
        ContractType.STAGE: "graduate",
        ContractType.ALTERNANCE: "graduate",
        ContractType.INTERIM: "contract",
        ContractType.FREELANCE: "contract",
    }

    SORT_MAPPING = {
        SortBy.RELEVANCE: "relevance",
        SortBy.DATE: "date",
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        cfg = config or {}
        self.app_id = cfg.get("app_id") or os.getenv("ADZUNA_APP_ID")
        self.app_key = cfg.get("app_key") or os.getenv("ADZUNA_APP_KEY")
        self.country = cfg.get("country", "fr")

        if not self.app_id or not self.app_key:
            logger.warning(
                "Clés API Adzuna non configurées: définir ADZUNA_APP_ID "
                "et ADZUNA_APP_KEY (voir .env.example)."
            )

    def search(self, criteria: SearchCriteria) -> Iterator[JobOffer]:
        if not self.app_id or not self.app_key:
            logger.error("Clés API Adzuna manquantes")
            return

        page = 1
        jobs_found = 0
        max_results = criteria.max_results
        seen_ids: set = set()
        results_per_page = 50  # Max autorisé par Adzuna

        while jobs_found < max_results:
            url, params = self._build_search_request(criteria, page, results_per_page)
            logger.debug(f"Requête Adzuna page {page}")

            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])
                if not results:
                    logger.info("Plus d'offres trouvées")
                    break

                new_jobs_on_page = 0
                for result in results:
                    if jobs_found >= max_results:
                        break

                    job = self._parse_result(result)
                    if job:
                        if job.id in seen_ids:
                            continue
                        seen_ids.add(job.id)
                        jobs_found += 1
                        new_jobs_on_page += 1
                        yield job

                if new_jobs_on_page == 0:
                    logger.info("Plus de nouvelles offres")
                    break

                total_count = data.get("count", 0)
                if page * results_per_page >= total_count:
                    break

                page += 1

            except requests.RequestException as e:
                # Ne pas logger l'URL complète: elle contient les clés API
                logger.error(f"Erreur API Adzuna: {type(e).__name__}")
                break
            except Exception as e:
                logger.error(f"Erreur lors de la recherche: {e}")
                break

        logger.info(f"Recherche terminée: {jobs_found} offres uniques trouvées")

    def get_job_details(self, job_id: str) -> Optional[JobOffer]:
        """Adzuna n'expose pas de détails supplémentaires via l'API."""
        return None

    def _build_search_request(
        self, criteria: SearchCriteria, page: int, results_per_page: int
    ) -> Tuple[str, dict]:
        """Construit l'URL et les paramètres (encodés par requests)."""
        url = f"{self.base_url}/{self.country}/search/{page}"

        params: dict = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": min(results_per_page, 50),
            "content-type": "application/json",
        }

        keywords_parts = []
        if criteria.title:
            keywords_parts.append(criteria.title)
        if criteria.keywords:
            keywords_parts.extend(criteria.keywords)
        if keywords_parts:
            params["what"] = " ".join(keywords_parts)

        if criteria.location and criteria.location != "France":
            params["where"] = criteria.location

        if criteria.radius_km:
            params["distance"] = criteria.radius_km

        if criteria.contract_types:
            contract_type = criteria.contract_types[0]
            if contract_type in self.CONTRACT_MAPPING:
                params["contract_type"] = self.CONTRACT_MAPPING[contract_type]
            if ContractType.CDI in criteria.contract_types:
                params["full_time"] = 1

        if criteria.date_posted == DatePosted.PAST_24H:
            params["max_days_old"] = 1
        elif criteria.date_posted == DatePosted.PAST_WEEK:
            params["max_days_old"] = 7
        elif criteria.date_posted == DatePosted.PAST_MONTH:
            params["max_days_old"] = 30

        if criteria.sort_by:
            params["sort_by"] = self.SORT_MAPPING.get(criteria.sort_by, "relevance")

        if criteria.salary_min:
            params["salary_min"] = int(criteria.salary_min)

        return url, params

    def _parse_result(self, result: dict) -> Optional[JobOffer]:
        """Parse un résultat de l'API Adzuna."""
        try:
            job_id = result.get("id")
            if not job_id:
                return None

            title = result.get("title", "").strip()
            company = result.get("company", {}).get("display_name", "").strip()
            location = result.get("location", {}).get("display_name", "").strip()

            if not title or not company:
                return None

            url = result.get("redirect_url", "")
            description = result.get("description", "")
            salary_min = result.get("salary_min")
            salary_max = result.get("salary_max")

            posted_at = None
            created = result.get("created")
            if created:
                try:
                    posted_at = datetime.fromisoformat(created.replace("Z", "+00:00"))
                except ValueError:
                    pass

            contract_type = None
            contract_data = result.get("contract_type")
            if contract_data == "permanent":
                contract_type = ContractType.CDI
            elif contract_data == "contract":
                contract_type = ContractType.CDD

            return JobOffer(
                id=f"adzuna_{job_id}",
                source=self.name,
                url=url,
                title=title,
                company=company,
                location=location or "France",
                description=description,
                salary_min=salary_min,
                salary_max=salary_max,
                contract_type=contract_type,
                posted_at=posted_at,
            )

        except Exception as e:
            logger.debug(f"Erreur parsing résultat Adzuna: {e}")
            return None
