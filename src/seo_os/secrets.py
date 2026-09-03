"""Secret-reference resolution without persistence or logging."""

from __future__ import annotations

import os
from typing import Mapping, Protocol


class SecretUnavailableError(RuntimeError):
    pass


class SecretResolver(Protocol):
    def available(self, reference: str) -> bool: ...

    def resolve(self, reference: str) -> str: ...


class EnvironmentSecretResolver:
    """Resolve environment-variable references; managed-secret URIs need an injected resolver."""

    def available(self, reference: str) -> bool:
        return not reference.startswith("secret://") and bool(os.environ.get(reference))

    def resolve(self, reference: str) -> str:
        if reference.startswith("secret://"):
            raise SecretUnavailableError("Managed-secret reference requires a configured resolver")
        value = os.environ.get(reference)
        if not value:
            raise SecretUnavailableError("Referenced environment secret is unavailable")
        return value


class MappingSecretResolver:
    """In-memory resolver for tests or host-managed secret injection."""

    def __init__(self, values: Mapping[str, str]) -> None:
        self._values = dict(values)

    def available(self, reference: str) -> bool:
        return bool(self._values.get(reference))

    def resolve(self, reference: str) -> str:
        value = self._values.get(reference)
        if not value:
            raise SecretUnavailableError("Referenced secret is unavailable")
        return value
