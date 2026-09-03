from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

from seo_os.connectors import ConnectorContext


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "connectors"


def fixture(name: str) -> Mapping[str, Any]:
    payload = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def authorization(
    *,
    provider: str,
    resource: str,
    fields: Sequence[str],
    methods: Sequence[str] = ("api",),
    authentication_method: str = "environment-secret",
    credential_reference: str | None = "FIXTURE_PROVIDER_ACCESS",
    record_types: Sequence[str] | None = None,
) -> dict[str, Any]:
    authorized_fields = list(fields)
    if provider == "pagespeed-insights":
        authorized_fields.extend(
            field for field in ("final_url", "fetch_time", "lighthouse_version", "audit_ids")
            if field not in authorized_fields
        )
    connector: dict[str, Any] = {
        "connector_id": f"{provider}-fixture",
        "provider": provider,
        "purpose": "Synthetic connector contract test",
        "authentication_method": authentication_method,
        "credential_reference": credential_reference,
        "acquisition_methods": list(methods),
        "access_mode": "read-only",
        "resource_ids": [resource],
        "allowed_fields": authorized_fields,
        "allowed_record_types": list(record_types or (_record_type_for(provider),)),
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "limitations": ["Synthetic test data only"],
    }
    return {
        "schema_version": "1.0.0",
        "authorization_id": "AUTHZ-FIXTURE-200",
        "project_id": "PROJECT-FIXTURE",
        "status": "active",
        "created_at": "2026-09-03T00:00:00Z",
        "expires_at": None,
        "authorized_by_reference": "synthetic-test-approval",
        "connectors": [connector],
        "data_minimization": {
            "purpose_limited": True,
            "pii_allowed": False,
            "retention_policy": "Delete synthetic artifacts after test",
        },
    }


def context(data_root: Path, manifest: Mapping[str, Any]) -> ConnectorContext:
    return ConnectorContext(
        project_id="PROJECT-FIXTURE",
        authorization_id="AUTHZ-FIXTURE-200",
        credential_reference=None,
        data_root=data_root,
        requested_at=datetime(2026, 9, 3, 9, 0, tzinfo=UTC),
        authorization_manifest=manifest,
    )


def _record_type_for(provider: str) -> str:
    return {
        "gsc": "gsc-search-performance",
        "ga4": "ga4-organic-landing-performance",
        "ahrefs": "ahrefs-organic-keywords",
        "pagespeed-insights": "psi-lab-performance",
        "crux": "crux-field-performance",
        "tabular": "generic-tabular-evidence",
    }[provider]
