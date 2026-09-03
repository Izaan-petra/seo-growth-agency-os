"""Conservative credential and PII redaction helpers."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any


REDACTED = "[REDACTED]"

_SENSITIVE_KEY = re.compile(
    r"(?i)^(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password|passwd|authorization(?:[_-]?header)?|cookie(?:[_-]?header)?|session(?:[_-]?(?:id|token|cookie))?|mfa|recovery[_-]?code)$"
)
_TEXT_PATTERNS = (
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"(?im)^(\s*[A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD)\s*=\s*)[^\s#][^\r\n]*$"),
    re.compile(r"(?i)(\"?(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password)\"?\s*[:=]\s*[\"'])[^\"'\r\n]{4,}([\"'])"),
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z0-9 ]*PRIVATE KEY-----"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
)


def redact_text(value: str) -> str:
    redacted = value
    for pattern in _TEXT_PATTERNS:
        if pattern.groups == 2:
            redacted = pattern.sub(rf"\1{REDACTED}\2", redacted)
        elif pattern.groups == 1:
            redacted = pattern.sub(rf"\1{REDACTED}", redacted)
        else:
            redacted = pattern.sub(REDACTED, redacted)
    return redacted


def redact_mapping(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: REDACTED if _SENSITIVE_KEY.search(str(key)) and item not in (None, "") else redact_mapping(item)
            for key, item in value.items()
        }
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [redact_mapping(item) for item in value]
    return value
