"""High-confidence repository secret and privacy scanning primitives."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PrivacyFinding:
    rule_id: str
    path: str
    line: int
    message: str


_RULES = (
    ("private-key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"), "Private key material"),
    ("bearer-token", re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{20,}"), "Bearer token value"),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}\b"), "GitHub token value"),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"), "AWS access key value"),
    (
        "credential-assignment",
        re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password)\s*[:=]\s*[\"']?[A-Za-z0-9/+_.=-]{12,}"),
        "Credential-like assignment",
    ),
)


def scan_text(text: str, path: str = "<memory>") -> tuple[PrivacyFinding, ...]:
    findings: list[PrivacyFinding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule_id, pattern, message in _RULES:
            if pattern.search(line):
                findings.append(PrivacyFinding(rule_id, path, line_number, message))
    return tuple(findings)


def scan_path(path: str | Path) -> tuple[PrivacyFinding, ...]:
    candidate = Path(path)
    try:
        text = candidate.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ()
    return scan_text(text, str(candidate))
