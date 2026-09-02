"""Read-only connector contracts and registry.

Provider-specific connectors are intentionally deferred to later Phase 3 batches.
"""

from .base import (
    AcquisitionRequest,
    Connector,
    ConnectorCapabilities,
    ConnectorContext,
    ConnectorError,
    ConnectorResult,
    ProbeResult,
)
from .registry import ConnectorRegistry

__all__ = [
    "AcquisitionRequest",
    "Connector",
    "ConnectorCapabilities",
    "ConnectorContext",
    "ConnectorError",
    "ConnectorRegistry",
    "ConnectorResult",
    "ProbeResult",
]
