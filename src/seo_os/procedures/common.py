"""Shared deterministic URL, query, date, evidence, and confidence utilities."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from datetime import date
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_PARAMETERS = {
    "fbclid", "gclid", "msclkid", "ref", "source",
    "utm_campaign", "utm_content", "utm_medium", "utm_source", "utm_term",
}
SENSITIVE_PARAMETERS = re.compile(r"(?i)(?:api[_-]?key|auth|authorization|cookie|password|secret|session|token)")


def stable_id(prefix: str, *parts: Any) -> str:
    canonical = json.dumps(parts, sort_keys=True, separators=(",", ":"), default=str)
    numeric = int(hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12], 16)
    return f"{prefix}-{numeric:015d}"


def normalize_query(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    normalized = re.sub(r"https?://\S+", " ", normalized)
    normalized = re.sub(r"[^\w\s-]", " ", normalized, flags=re.UNICODE)
    normalized = re.sub(r"[_\s-]+", " ", normalized).strip()
    return normalized


def query_tokens(value: str) -> frozenset[str]:
    return frozenset(token for token in normalize_query(value).split() if token)


def lexical_overlap(left: str, right: str) -> float:
    a, b = query_tokens(left), query_tokens(right)
    return len(a & b) / len(a | b) if a or b else 1.0


def canonicalize_url(value: str, *, remove_tracking: bool = True) -> str:
    parsed = urlsplit(value.strip())
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    port = parsed.port
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    query = parse_qsl(parsed.query, keep_blank_values=True)
    if remove_tracking:
        query = [
            (key, val) for key, val in query
            if key.casefold() not in TRACKING_PARAMETERS and not SENSITIVE_PARAMETERS.search(key)
        ]
    return urlunsplit((scheme, host, path, urlencode(sorted(query)), ""))


def domain_of(value: str) -> str:
    return (urlsplit(value).hostname or "").casefold()


def parse_iso_date(value: Any) -> date:
    if not isinstance(value, str):
        raise ValueError("Date must use YYYY-MM-DD")
    return date.fromisoformat(value)


def period_days(period: Mapping[str, Any] | None) -> int | None:
    if not period:
        return None
    try:
        return (parse_iso_date(period["end_date"]) - parse_iso_date(period["start_date"])).days + 1
    except (KeyError, TypeError, ValueError):
        return None


def percent_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return (current - previous) / abs(previous)


def as_number(value: Any) -> float | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().casefold()
        if lowered in {"true", "yes", "1", "allowed", "index"}:
            return True
        if lowered in {"false", "no", "0", "blocked", "noindex"}:
            return False
    return None


def values(record: Mapping[str, Any]) -> Mapping[str, Any]:
    nested = record.get("values")
    return nested if isinstance(nested, Mapping) else record


def classify_cwv(metric: str, p75: float) -> str:
    thresholds = {
        "largest_contentful_paint": (2500.0, 4000.0),
        "interaction_to_next_paint": (200.0, 500.0),
        "cumulative_layout_shift": (0.1, 0.25),
    }
    if metric not in thresholds:
        raise ValueError(f"Unsupported Core Web Vital: {metric}")
    good, poor = thresholds[metric]
    return "good" if p75 <= good else "needs-improvement" if p75 <= poor else "poor"


def evidence_tier(source: str, provenance: Mapping[str, Any]) -> str:
    declared = provenance.get("evidence_tier")
    if declared in {"first-party", "third-party", "public"}:
        return str(declared)
    if source in {"gsc", "ga4"}:
        return "first-party"
    if source == "ahrefs":
        return "third-party"
    return "public"


def confidence_for(*, direct: bool, tiers: Iterable[str], degraded: bool = False) -> str:
    tier_set = set(tiers)
    if degraded:
        return "low"
    if direct and "first-party" in tier_set:
        return "high"
    if direct or len(tier_set) > 1:
        return "medium"
    return "low"


def deduplicate_preserving_order(items: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in items if item))
