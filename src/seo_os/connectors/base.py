"""Provider-neutral, read-only connector interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re
from typing import Any, Mapping


class ConnectorError(RuntimeError):
    """A safe connector failure that must not contain credential values."""

    def __init__(self, category: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.category = category
        self.retryable = retryable


@dataclass(frozen=True, slots=True)
class ConnectorCapabilities:
    provider: str
    acquisition_methods: tuple[str, ...]
    authentication_methods: tuple[str, ...]
    supported_record_types: tuple[str, ...]
    read_only: bool = True

    def __post_init__(self) -> None:
        if not self.read_only:
            raise ValueError("SEO OS connectors must be read-only")
        if not self.provider.strip():
            raise ValueError("Connector provider is required")


@dataclass(frozen=True, slots=True)
class ConnectorContext:
    project_id: str
    authorization_id: str
    credential_reference: str | None
    data_root: Path
    requested_at: datetime
    approved_resource_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.credential_reference is not None and re.fullmatch(
            r"(?:[A-Z][A-Z0-9_]{2,127}|secret://[A-Za-z0-9._/-]+)",
            self.credential_reference,
        ) is None:
            raise ValueError(
                "credential_reference must be an environment-variable name or managed-secret reference"
            )


@dataclass(frozen=True, slots=True)
class AcquisitionRequest:
    source: str
    record_type: str
    resource_id: str
    fields: tuple[str, ...]
    start_date: str | None = None
    end_date: str | None = None
    filters: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source.strip() or not self.record_type.strip() or not self.resource_id.strip():
            raise ValueError("Acquisition source, record type, and resource are required")
        if not self.fields:
            raise ValueError("At least one acquisition field is required")


@dataclass(frozen=True, slots=True)
class ProbeResult:
    available: bool
    authorized: bool
    acquisition_methods: tuple[str, ...]
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ConnectorResult:
    source: str
    acquisition_method: str
    retrieved_at: datetime
    records: tuple[Mapping[str, Any], ...]
    limitations: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


class Connector(ABC):
    """Base class for minimum-scope data collection.

    Connectors execute an intake-approved acquisition request. They do not select
    sources, broaden scope, request credentials, or mutate external systems.
    """

    @property
    @abstractmethod
    def capabilities(self) -> ConnectorCapabilities:
        """Describe supported read-only behavior."""

    @abstractmethod
    def probe(self, context: ConnectorContext) -> ProbeResult:
        """Report availability without returning or logging secret values."""

    @abstractmethod
    def collect(
        self, context: ConnectorContext, request: AcquisitionRequest
    ) -> ConnectorResult:
        """Collect only the authorized resource and requested fields."""
