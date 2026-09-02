"""Ingestion contracts, validation, quality, and snapshots."""

from .manifest import IngestionManifest, load_ingestion_manifest, write_ingestion_manifest
from .normalization import NormalizedRecord, Normalizer, NormalizationError
from .quality import DataQualityCheck, QualityIssue, QualityReport, QualityStatus
from .snapshot import SnapshotDescriptor, SnapshotStore, sha256_file

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
    "load_ingestion_manifest",
    "sha256_file",
    "write_ingestion_manifest",
]
