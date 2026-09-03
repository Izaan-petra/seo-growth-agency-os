"""Read-only connector contracts, Batch 2 adapters, and registry."""

from .base import (
    AcquisitionRequest,
    Connector,
    ConnectorCapabilities,
    ConnectorContext,
    ConnectorError,
    ConnectorResult,
    ProbeResult,
)
from .transport import FixtureTransport, HttpResponse, HttpTransport, UrllibJsonTransport
from .registry import ConnectorRegistry


def build_default_registry(*, transport=None, secret_resolver=None):
    """Load and register Batch 2 providers only when the catalog is requested."""
    from .catalog import build_default_registry as build

    return build(transport=transport, secret_resolver=secret_resolver)

__all__ = [
    "AcquisitionRequest",
    "Connector",
    "ConnectorCapabilities",
    "ConnectorContext",
    "ConnectorError",
    "ConnectorRegistry",
    "ConnectorResult",
    "FixtureTransport",
    "HttpResponse",
    "HttpTransport",
    "ProbeResult",
    "UrllibJsonTransport",
    "build_default_registry",
]
