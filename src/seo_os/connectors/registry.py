"""Deterministic connector registration without provider imports."""

from __future__ import annotations

from collections.abc import Iterable

from .base import Connector


class ConnectorRegistry:
    def __init__(self, connectors: Iterable[Connector] = ()) -> None:
        self._connectors: dict[str, Connector] = {}
        for connector in connectors:
            self.register(connector)

    def register(self, connector: Connector) -> None:
        provider = connector.capabilities.provider
        if provider in self._connectors:
            raise ValueError(f"Connector already registered: {provider}")
        if not connector.capabilities.read_only:
            raise ValueError(f"Connector is not read-only: {provider}")
        self._connectors[provider] = connector

    def get(self, provider: str) -> Connector:
        try:
            return self._connectors[provider]
        except KeyError as exc:
            raise KeyError(f"Unknown connector: {provider}") from exc

    def providers(self) -> tuple[str, ...]:
        return tuple(sorted(self._connectors))

    def __contains__(self, provider: object) -> bool:
        return provider in self._connectors

    def __len__(self) -> int:
        return len(self._connectors)
