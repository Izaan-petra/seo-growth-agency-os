"""Minimal local developer CLI for authorization, connectors, exports, and fixtures."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence

from seo_os.authorization import AuthorizationManifest
from seo_os.connectors import AcquisitionRequest, ConnectorContext, FixtureTransport, build_default_registry
from seo_os.ingestion import validate_snapshot_payload
from seo_os.security.redaction import redact_mapping
from seo_os.secrets import MappingSecretResolver


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command == "connectors":
        registry = build_default_registry()
        for provider in registry.providers():
            capabilities = registry.get(provider).capabilities
            _print_json({"provider": provider, "read_only": capabilities.read_only, "acquisition_methods": capabilities.acquisition_methods, "record_types": capabilities.supported_record_types})
        return 0
    if args.command == "validate-authorization":
        manifest = AuthorizationManifest.from_path(args.path)
        _print_json({"authorization_id": manifest.payload["authorization_id"], "status": manifest.payload["status"], "valid": True})
        return 0
    if args.command == "validate-snapshot":
        payload = _json_object(args.path)
        validate_snapshot_payload(payload)
        _print_json({"snapshot_id": payload["snapshot_id"], "valid": True})
        return 0
    if args.command in {"ingest-export", "mock-connector"}:
        manifest = AuthorizationManifest.from_path(args.authorization)
        if args.command == "mock-connector":
            fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
            responses = fixture if isinstance(fixture, list) else [fixture]
            if not all(isinstance(item, dict) for item in responses):
                raise ValueError("Mock fixture must contain an object or array of objects")
            references = {
                item["credential_reference"]: "mock-runtime-value"
                for item in manifest.payload["connectors"]
                if item.get("credential_reference")
            }
            registry = build_default_registry(
                transport=FixtureTransport(responses), secret_resolver=MappingSecretResolver(references)
            )
            provider = args.provider
            filters = _json_argument(args.filters)
        else:
            registry = build_default_registry()
            provider = "tabular"
            filters = {
                "path": args.file,
                "sheet": args.sheet,
                "field_mapping": _json_argument(args.field_mapping),
                "required_fields": _csv_values(args.fields),
            }
        context = ConnectorContext(
            project_id=manifest.payload["project_id"],
            authorization_id=manifest.payload["authorization_id"],
            credential_reference=None,
            data_root=args.data_root,
            requested_at=datetime.now(UTC),
            authorization_manifest=manifest.payload,
        )
        request = AcquisitionRequest(
            source=provider, record_type=args.record_type, resource_id=args.resource,
            fields=_csv_values(args.fields), start_date=args.start_date,
            end_date=args.end_date, filters=filters,
        )
        result = registry.get(provider).collect(context, request)
        _print_json({"status": result.status, "rows": len(result.records), "rejected_rows": len(result.rejected_records), "metadata": result.metadata, "errors": result.errors, "snapshot": result.snapshot}, indent=2)
        return 0 if result.status != "failed" else 1
    parser.error("Unknown command")
    return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="seo-os", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("connectors", help="List registered read-only connectors")
    auth = commands.add_parser("validate-authorization", help="Validate an authorization manifest")
    auth.add_argument("path", type=Path)
    snapshot = commands.add_parser("validate-snapshot", help="Validate snapshot identity and required fields")
    snapshot.add_argument("path", type=Path)

    export = commands.add_parser("ingest-export", help="Ingest an authorized CSV/XLSX export under DATA_ROOT/raw")
    _common_acquisition_arguments(export, provider=False)
    export.add_argument("--file", required=True, help="Path relative to DATA_ROOT/raw")
    export.add_argument("--sheet")
    export.add_argument("--field-mapping", default="{}", help="JSON source-to-canonical header map")

    mock = commands.add_parser("mock-connector", help="Run a connector against JSON fixture responses only")
    _common_acquisition_arguments(mock, provider=True)
    mock.add_argument("--fixture", required=True, type=Path)
    mock.add_argument("--filters", default="{}", help="JSON acquisition filters")
    return parser


def _common_acquisition_arguments(parser: argparse.ArgumentParser, *, provider: bool) -> None:
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--data-root", required=True, type=Path)
    if provider:
        parser.add_argument("--provider", required=True)
    parser.add_argument("--record-type", required=True)
    parser.add_argument("--resource", required=True)
    parser.add_argument("--fields", required=True, help="Comma-separated authorized fields")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")


def _json_argument(value: str) -> dict[str, Any]:
    payload = json.loads(value)
    if not isinstance(payload, dict):
        raise ValueError("JSON argument must be an object")
    return payload


def _json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON document must be an object")
    return payload


def _csv_values(value: str) -> tuple[str, ...]:
    result = tuple(item.strip() for item in value.split(",") if item.strip())
    if not result:
        raise ValueError("At least one field is required")
    return result


def _print_json(payload: Any, *, indent: int | None = None) -> None:
    """Emit a final redacted JSON boundary for every CLI response."""

    print(json.dumps(redact_mapping(payload), indent=indent, sort_keys=True, default=str))
