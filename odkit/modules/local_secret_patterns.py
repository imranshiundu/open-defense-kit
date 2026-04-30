"""Local-only secret pattern review.

This is a defensive helper for scanning files you own. It does not send data to
any network service and does not attempt to validate discovered values.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


PATTERNS: dict[str, re.Pattern[str]] = {
    "generic_api_key": re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?([a-z0-9_\-]{16,})"),
    "private_key_marker": re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "aws_access_key_like": re.compile(r"AKIA[0-9A-Z]{16}"),
}

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}
TEXT_SUFFIXES = {
    ".env",
    ".txt",
    ".md",
    ".py",
    ".js",
    ".ts",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    pattern: str
    preview: str


def should_scan(path: Path) -> bool:
    """Return True if a path should be scanned as text."""

    if any(part in SKIP_DIRS for part in path.parts):
        return False
    return path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name == ".env")


def redact(line: str) -> str:
    """Redact long values from a finding preview."""

    stripped = line.strip()
    if len(stripped) <= 24:
        return stripped
    return f"{stripped[:12]}...[redacted]...{stripped[-6:]}"


def scan_path(root: Path) -> list[Finding]:
    """Scan a local path for common secret-like patterns."""

    findings: list[Finding] = []
    candidates = [root] if root.is_file() else root.rglob("*")

    for path in candidates:
        if not should_scan(path):
            continue

        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue

        for line_no, line in enumerate(lines, start=1):
            for name, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        Finding(
                            path=str(path),
                            line=line_no,
                            pattern=name,
                            preview=redact(line),
                        )
                    )
    return findings
