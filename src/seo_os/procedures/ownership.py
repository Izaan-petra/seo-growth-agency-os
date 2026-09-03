"""Programmatic cross-specialist ownership rules for shared fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class OwnershipRule:
    primary_owner: str
    contributors: tuple[str, ...]
    final_decision_owner: str = "seo-director"


OWNERSHIP_RULES: Mapping[str, OwnershipRule] = {
    "internal-link-structure": OwnershipRule("technical-seo", ("keyword-intent-strategy", "seo-content-strategy")),
    "internal-link-context": OwnershipRule("seo-content-strategy", ("technical-seo", "keyword-intent-strategy")),
    "cannibalization": OwnershipRule("keyword-intent-strategy", ("seo-content-strategy", "technical-seo")),
    "structured-data-validity": OwnershipRule("technical-seo", ("geo-aeo", "seo-content-strategy")),
    "structured-data-entity-alignment": OwnershipRule("geo-aeo", ("technical-seo", "seo-content-strategy")),
    "cta-and-form-friction": OwnershipRule("seo-cro", ("seo-content-strategy",)),
    "analytics-acquisition-metadata": OwnershipRule("project-intake", ("seo-measurement",)),
    "analytics-kpi-interpretation": OwnershipRule("seo-measurement", ("project-intake", "seo-cro")),
    "implementation-validation": OwnershipRule("seo-director", ("seo-measurement",)),
}


def ownership_for(field: str) -> OwnershipRule:
    try:
        return OWNERSHIP_RULES[field]
    except KeyError as exc:
        raise KeyError(f"Unknown shared SEO field: {field}") from exc


def assert_owner(field: str, workstream: str) -> None:
    rule = ownership_for(field)
    if workstream != rule.primary_owner:
        raise ValueError(f"{workstream} cannot emit the canonical {field} finding; owner is {rule.primary_owner}")
