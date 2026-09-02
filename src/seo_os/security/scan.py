"""Command-line high-confidence secret scanner."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Sequence

from .privacy import scan_path


def _staged_paths(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [root / line for line in result.stdout.splitlines() if line.strip()]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args(argv)
    root = Path.cwd()
    paths = _staged_paths(root) if args.staged else args.paths
    findings = [finding for path in paths for finding in scan_path(path)]
    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.rule_id}: {finding.message}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
