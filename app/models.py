"""Modèles de données pour les offres d'emploi."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ContractType(str, Enum):
    """Types de contrat."""
    CDI = "cdi"
    CDD = "cdd"
    INTERIM = "interim"
    STAGE = "stage"
    ALTERNANCE = "alternance"
    FREELANCE = "freelance"
    OTHER = "other"


class ExperienceLevel(str, Enum):
    """Niveaux d'expérience."""
    INTERNSHIP = "internship"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    DIRECTOR = "director"


class WorkplaceType(str, Enum):
    """Type de lieu de travail."""
    ON_SITE = "on_site"
    REMOTE = "remote"
    HYBRID = "hybrid"


class DatePosted(str, Enum):
    """Filtre par date de publication."""
    PAST_24H = "past_24h"
    PAST_WEEK = "past_week"
    PAST_MONTH = "past_month"
    ANY_TIME = "any_time"


class SortBy(str, Enum):
    """Tri des résultats."""
    RELEVANCE = "relevance"
    DATE = "date"


class JobOffer(BaseModel):
    """Modèle représentant une offre d'emploi."""

    id: str = Field(..., description="Identifiant unique de l'offre")
    source: str = Field(..., description="Source de l'offre")
    url: HttpUrl = Field(..., description="URL de l'offre")

    title: str = Field(..., description="Titre du poste")
    company: str = Field(..., description="Nom de l'entreprise")
    location: str = Field(..., description="Localisation du poste")

    description: Optional[str] = Field(None, description="Description du poste")
    salary_min: Optional[float] = Field(None, description="Salaire minimum")
    salary_max: Optional[float] = Field(None, description="Salaire maximum")
    salary_currency: str = Field(default="EUR", description="Devise du salaire")

    contract_type: Optional[ContractType] = Field(None, description="Type de contrat")
    experience_level: Optional[ExperienceLevel] = Field(None, description="Niveau d'expérience")
    remote: Optional[bool] = Field(None, description="Possibilité de télétravail")

    posted_at: Optional[datetime] = Field(None, description="Date de publication")
    scraped_at: datetime = Field(default_factory=datetime.now, description="Date de scraping")

    skills: List[str] = Field(default_factory=list, description="Compétences requises")
    benefits: List[str] = Field(default_factory=list, description="Avantages proposés")


class SearchCriteria(BaseModel):
    """Critères de recherche d'offres d'emploi."""

    keywords: List[str] = Field(default_factory=list, description="Mots-clés de recherche")
    title: Optional[str] = Field(None, description="Titre de poste exact")
    location: str = Field(default="France", description="Localisation recherchée")
    radius_km: Optional[int] = Field(None, description="Rayon de recherche en km")

    contract_types: List[ContractType] = Field(default_factory=list, description="Types de contrat")
    experience_levels: List[ExperienceLevel] = Field(default_factory=list, description="Niveaux d'expérience")
    workplace_types: List[WorkplaceType] = Field(default_factory=list, description="Types de lieu de travail")

    date_posted: Optional[DatePosted] = Field(None, description="Date de publication")

    companies: List[str] = Field(default_factory=list, description="Entreprises spécifiques")
    exclude_companies: List[str] = Field(default_factory=list, description="Entreprises à exclure")

    salary_min: Optional[int] = Field(None, description="Salaire minimum souhaité")

    sort_by: SortBy = Field(default=SortBy.RELEVANCE, description="Tri des résultats")
    max_results: int = Field(default=100, description="Nombre maximum de résultats")
