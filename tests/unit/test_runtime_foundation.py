from __future__ import annotations

import io
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from seo_os.connectors import (
    AcquisitionRequest,
    Connector,
    ConnectorCapabilities,
    ConnectorContext,
    ConnectorRegistry,
    ConnectorResult,
    ProbeResult,
)
from seo_os.ingestion import (
    IngestionManifest,
    QualityIssue,
    QualityReport,
    QualityStatus,
    load_ingestion_manifest,
    sha256_file,
    write_ingestion_manifest,
)


class DummyConnector(Connector):
    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            provider="fixture",
            acquisition_methods=("export",),
            authentication_methods=("none",),
            supported_record_types=("fixture-record",),
        )

    def probe(self, context: ConnectorContext) -> ProbeResult:
        return ProbeResult(True, True, ("export",))

    def collect(
        self, context: ConnectorContext, request: AcquisitionRequest
    ) -> ConnectorResult:
        return ConnectorResult(
            source="fixture",
            acquisition_method="export",
            retrieved_at=datetime.now(UTC),
            records=({"field": "value"},),
        )


class RuntimeFoundationTests(unittest.TestCase):
    def test_registry_accepts_read_only_connector_once(self) -> None:
        registry = ConnectorRegistry([DummyConnector()])
        self.assertEqual(("fixture",), registry.providers())
        self.assertIsInstance(registry.get("fixture"), DummyConnector)
        with self.assertRaises(ValueError):
            registry.register(DummyConnector())

    def test_connector_capabilities_reject_write_mode(self) -> None:
        with self.assertRaises(ValueError):
            ConnectorCapabilities("unsafe", (), (), (), read_only=False)

    def test_connector_context_accepts_reference_not_secret_value(self) -> None:
        context = ConnectorContext(
            project_id="PROJECT-FIXTURE",
            authorization_id="AUTHZ-FIXTURE-001",
            credential_reference="FIXTURE_API_KEY",
            data_root=Path("research"),
            requested_at=datetime.now(UTC),
        )
        self.assertEqual("FIXTURE_API_KEY", context.credential_reference)
        with self.assertRaises(ValueError):
            ConnectorContext(
                project_id="PROJECT-FIXTURE",
                authorization_id="AUTHZ-FIXTURE-001",
                credential_reference="actual-secret-looking-value",
                data_root=Path("research"),
                requested_at=datetime.now(UTC),
            )

    def test_ingestion_manifest_round_trip_is_validated(self) -> None:
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "schemas" / "ingestion-manifest.json"
        manifest = load_ingestion_manifest(fixture)
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "manifest.json"
            write_ingestion_manifest(destination, manifest)
            loaded = load_ingestion_manifest(destination)
        self.assertEqual(manifest.as_dict(), loaded.as_dict())

    def test_quality_report_fails_closed(self) -> None:
        report = QualityReport(
            "fixture",
            "fixture-record",
            (QualityIssue("missing-field", QualityStatus.FAIL, "Required field absent"),),
        )
        self.assertEqual(QualityStatus.FAIL, report.status)
        self.assertFalse(report.usable)

    def test_sha256_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "value.txt"
            path.write_text("seo-os", encoding="utf-8")
            self.assertEqual(64, len(sha256_file(path)))


if __name__ == "__main__":
    unittest.main()
