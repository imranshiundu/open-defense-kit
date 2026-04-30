"""Legacy migration classifier for Open Defense Kit.

This module performs static classification only. It does not execute legacy code.
The goal is to decide whether legacy files/features should be rewritten,
documented, removed, or prohibited.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class MigrationDecision(str, Enum):
    """Supported migration decisions."""

    KEEP_SAFE = "KEEP_SAFE"
    REWRITE_SAFE = "REWRITE_SAFE"
    DOCS_ONLY = "DOCS_ONLY"
    LAB_ONLY_DOCS = "LAB_ONLY_DOCS"
    REMOVE = "REMOVE"
    PROHIBITED = "PROHIBITED"


@dataclass(frozen=True)
class ClassificationRule:
    """A static rule used to classify legacy content."""

    decision: MigrationDecision
    reason: str
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class FileClassification:
    """Classification result for one legacy file."""

    path: str
    decision: MigrationDecision
    reason: str
    matched_tokens: tuple[str, ...]


RULES: tuple[ClassificationRule, ...] = (
    ClassificationRule(
        decision=MigrationDecision.PROHIBITED,
        reason="phishing, social engineering automation, or credential deception is not allowed",
        tokens=("phish", "setoolkit", "evilginx", "social engineering", "credential harvest"),
    ),
    ClassificationRule(
        decision=MigrationDecision.PROHIBITED,
        reason="DDoS or service disruption tooling is not allowed",
        tokens=("ddos", "slowloris", "hulk", "goldeneye", "xerxes", "dos attack"),
    ),
    ClassificationRule(
        decision=MigrationDecision.PROHIBITED,
        reason="RAT/C2/backdoor/post-exploitation automation is not allowed",
        tokens=(" rat", "c2", "backdoor", "meterpreter", "post-exploitation", "reverse shell"),
    ),
    ClassificationRule(
        decision=MigrationDecision.PROHIBITED,
        reason="payload building/deployment is not allowed",
        tokens=("payload", "msfvenom", "venom", "apk payload"),
    ),
    ClassificationRule(
        decision=MigrationDecision.PROHIBITED,
        reason="camera/webcam/device spying functionality is not allowed",
        tokens=("camera hack", "webcam", "cam hack", "spy camera"),
    ),
    ClassificationRule(
        decision=MigrationDecision.LAB_ONLY_DOCS,
        reason="credential attack concepts may be explained only in isolated lab/awareness documentation",
        tokens=("bruteforce", "brute force", "hydra", "medusa", "password attack", "crack password"),
    ),
    ClassificationRule(
        decision=MigrationDecision.LAB_ONLY_DOCS,
        reason="exploit tooling must not be automated against live targets; lab documentation only",
        tokens=("sqlmap", "exploit", "metasploit", "sqli", "xss"),
    ),
    ClassificationRule(
        decision=MigrationDecision.LAB_ONLY_DOCS,
        reason="wireless attack concepts can disrupt networks; lab documentation only",
        tokens=("aircrack", "deauth", "evil twin", "wifi attack", "wifite"),
    ),
    ClassificationRule(
        decision=MigrationDecision.REMOVE,
        reason="unsafe installer/update pattern should be removed, not migrated",
        tokens=("sudo", "su ", "git clone", "curl", "wget", "rm -rf", "rm -r", "install.sh"),
    ),
    ClassificationRule(
        decision=MigrationDecision.REWRITE_SAFE,
        reason="defensive scanning/audit concept can be rewritten safely with permission gates",
        tokens=("secret", "dependency", "headers", "container", "trivy", "prowler", "scoutsuite", "osint"),
    ),
    ClassificationRule(
        decision=MigrationDecision.DOCS_ONLY,
        reason="educational material can remain as documentation if rewritten ethically",
        tokens=("tutorial", "guide", "notes", "learning", "education"),
    ),
)

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

DECISION_PRIORITY: dict[MigrationDecision, int] = {
    MigrationDecision.PROHIBITED: 100,
    MigrationDecision.REMOVE: 80,
    MigrationDecision.LAB_ONLY_DOCS: 70,
    MigrationDecision.REWRITE_SAFE: 50,
    MigrationDecision.DOCS_ONLY: 30,
    MigrationDecision.KEEP_SAFE: 10,
}


def is_text_candidate(path: Path) -> bool:
    """Return True when a file should be classified as text."""

    return path.is_file() and path.suffix.lower() in TEXT_SUFFIXES


def classify_text(path: str, content: str) -> FileClassification:
    """Classify one text blob."""

    lowered = content.lower()
    best_decision = MigrationDecision.KEEP_SAFE
    best_reason = "no risky or migration-specific patterns found"
    matched: list[str] = []

    for rule in RULES:
        hits = [token for token in rule.tokens if token in lowered]
        if not hits:
            continue

        if DECISION_PRIORITY[rule.decision] > DECISION_PRIORITY[best_decision]:
            best_decision = rule.decision
            best_reason = rule.reason
            matched = hits
        elif rule.decision == best_decision:
            matched.extend(hits)

    return FileClassification(
        path=path,
        decision=best_decision,
        reason=best_reason,
        matched_tokens=tuple(sorted(set(matched))),
    )


def classify_path(root: Path) -> list[FileClassification]:
    """Classify legacy files under a path."""

    results: list[FileClassification] = []
    candidates = [root] if root.is_file() else root.rglob("*")

    for path in candidates:
        if not is_text_candidate(path):
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        results.append(classify_text(str(path), content))

    return results


def classifications_to_markdown(results: list[FileClassification]) -> str:
    """Render classification results as markdown."""

    output = ["# Legacy Migration Classification", ""]
    if not results:
        output.append("No text files were found to classify.")
        return "\n".join(output)

    counts: dict[MigrationDecision, int] = {decision: 0 for decision in MigrationDecision}
    for result in results:
        counts[result.decision] += 1

    output.append("## Summary")
    output.append("")
    output.append("| Decision | Count |")
    output.append("|---|---:|")
    for decision in MigrationDecision:
        output.append(f"| `{decision.value}` | {counts[decision]} |")

    output.append("")
    output.append("## File decisions")
    output.append("")
    output.append("| File | Decision | Reason | Matched tokens |")
    output.append("|---|---|---|---|")

    for result in results:
        tokens = ", ".join(f"`{token}`" for token in result.matched_tokens) or "—"
        reason = result.reason.replace("|", "\\|")
        output.append(f"| `{result.path}` | `{result.decision.value}` | {reason} | {tokens} |")

    output.append("")
    output.append("## Migration rule")
    output.append("")
    output.append("Do not run files from `legacy/original/`. Rewrite approved safe ideas under `odkit/` with safety metadata, docs, tests, and permission gates.")
    return "\n".join(output)
