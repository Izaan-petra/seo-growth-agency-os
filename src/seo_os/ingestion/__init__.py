"""Ingestion contracts, validation, quality, and snapshots."""

from .manifest import IngestionManifest, load_ingestion_manifest, write_ingestion_manifest
from .normalization import NormalizedRecord, Normalizer, NormalizationError
from .quality import (
    DataQualityCheck,
    QualityIssue,
    QualityReport,
    QualityStatus,
    quality_report_as_dict,
    validate_records,
)
from .snapshot import (
    SnapshotDescriptor,
    SnapshotStore,
    deterministic_snapshot_id,
    sha256_file,
    validate_snapshot_payload,
    write_immutable_json,
)

__all__ = [
    "DataQualityCheck",
    "IngestionManifest",
    "NormalizedRecord",
    "Normalizer",
    "NormalizationError",
    "QualityIssue",
    "QualityReport",
    "QualityStatus",
    "SnapshotDescriptor",
    "SnapshotStore",
    "deterministic_snapshot_id",
    "load_ingestion_manifest",
    "quality_report_as_dict",
    "sha256_file",
    "validate_records",
    "validate_snapshot_payload",
    "write_immutable_json",
    "write_ingestion_manifest",
]
