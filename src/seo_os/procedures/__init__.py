"""Deterministic, snapshot-driven SEO specialist procedures."""

from .authority import run_authority_procedure
from .content import run_content_procedure
from .cro import run_cro_procedure
from .geo import run_geo_procedure
from .keyword import run_keyword_procedure
from .measurement import run_measurement_procedure
from .serp import run_serp_procedure
from .technical import run_technical_procedure

PROCEDURES = {
    "authority-link-building": run_authority_procedure,
    "competitor-serp-analysis": run_serp_procedure,
    "geo-aeo": run_geo_procedure,
    "keyword-intent-strategy": run_keyword_procedure,
    "seo-content-strategy": run_content_procedure,
    "seo-cro": run_cro_procedure,
    "seo-measurement": run_measurement_procedure,
    "technical-seo": run_technical_procedure,
}


def get_procedure(workstream: str):
    """Return the registered Batch 3 procedure or fail closed."""
    try:
        return PROCEDURES[workstream]
    except KeyError as exc:
        raise KeyError(f"No deterministic procedure is registered for: {workstream}") from exc

__all__ = [
    "run_authority_procedure",
    "run_content_procedure",
    "run_cro_procedure",
    "run_geo_procedure",
    "run_keyword_procedure",
    "run_measurement_procedure",
    "run_serp_procedure",
    "run_technical_procedure",
    "PROCEDURES",
    "get_procedure",
]
