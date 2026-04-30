"""Static audit helper for quarantined legacy code.

This module only reads files and reports risky strings. It does not execute
legacy code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


RISK_PATTERNS: dict[str, str] = {
    "root_or_privilege": "sudo/su/root usage",
    "blind_clone": "blind git clone behavior",
    "remote_script": "remote download or shell execution",
    "raw_shell": "raw shell execution",
    "destructive_delete": "destructive delete pattern",
    "phishing": "phishing/social engineering reference",
    "ddos": "DDoS/disruption reference",
    "rat_c2": "RAT/C2/post-exploitation reference",
    "payload": "payload builder/deployment reference",
    "credential_attack": "credential attack/bruteforce reference",
    "camera_hacking": "camera/webcam hacking reference",
}

PATTERN_TOKENS: dict[str, tuple[str, ...]] = {
    "root_or_privilege": ("sudo", "su ", "root"),
    "blind_clone": ("git clone",),
    "remote_script": ("curl", "wget", "| sh", "| bash"),
    "raw_shell": ("os.system", "subprocess", "shell=True"),
    "destructive_delete": ("rm -rf", "rm -r", "shutil.rmtree"),
    "phishing": ("phish", "social engineering", "setoolkit", "evilginx"),
    "ddos": ("ddos", "dos attack", "slowloris", "hulk"),
    "rat_c2": ("rat", "c2", "meterpreter", "post-exploitation", "backdoor"),
    "payload": ("payload", "msfvenom"),
    "credential_attack": ("bruteforce", "brute force", "hydra", "crack", "password attack"),
    "camera_hacking": ("camera", "webcam", "cam hack"),
}

TEXT_SUFFIXES = {
    "",
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".txt",
    ".md",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".cfg",
    ".ini",
}


@dataclass(frozen=True)
class LegacyFinding:
    path: str
    line: int
    category: str
    description: str
    preview: str


def is_text_candidate(path: Path) -> bool:
    """Return True when a file should be read as text."""

    return path.is_file() and path.suffix.lower() in TEXT_SUFFIXES


def audit_legacy_path(root: Path) -> list[LegacyFinding]:
    """Perform static pattern review of a legacy file or directory."""

    findings: list[LegacyFinding] = []
    candidates = [root] if root.is_file() else root.rglob("*")

    for path in candidates:
        if not is_text_candidate(path):
            continue

        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue

        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            for category, tokens in PATTERN_TOKENS.items():
                if any(token in lowered for token in tokens):
                    findings.append(
                        LegacyFinding(
                            path=str(path),
                            line=line_number,
                            category=category,
                            description=RISK_PATTERNS[category],
                            preview=line.strip()[:180],
                        )
                    )
    return findings


def findings_to_markdown(findings: list[LegacyFinding]) -> str:
    """Render findings as markdown."""

    if not findings:
        return "# Legacy Static Audit Report\n\nNo risky patterns found by the basic static scanner.\n"

    output = ["# Legacy Static Audit Report", "", f"Findings: {len(findings)}", ""]
    output.append("| File | Line | Category | Description | Preview |")
    output.append("|---|---:|---|---|---|")

    for finding in findings:
        preview = finding.preview.replace("|", "\\|")
        output.append(
            f"| `{finding.path}` | {finding.line} | `{finding.category}` | {finding.description} | `{preview}` |"
        )

    output.append("")
    output.append("## Reminder")
    output.append("")
    output.append("This is a static pattern scan only. It does not prove code is safe or unsafe by itself.")
    return "\n".join(output)
