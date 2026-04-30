"""Command safety guard for Open Defense Kit.

This module does not execute commands. It classifies command argument arrays so
future module runners can block dangerous patterns before anything runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field


BLOCKED_EXECUTABLES = {
    "sudo",
    "su",
    "bash",
    "sh",
    "zsh",
    "fish",
    "curl",
    "wget",
    "nc",
    "netcat",
    "ncat",
}

BLOCKED_TOKENS = {
    "rm -rf",
    "mkfs",
    ":(){",
    "dd if=",
    "chmod 777",
    "chown -R",
    "curl | sh",
    "curl|sh",
    "wget | sh",
    "wget|sh",
    "git clone",
    "pip install git+",
}

NETWORK_TOOLS_REQUIRING_REVIEW = {
    "nmap",
    "masscan",
    "amass",
    "subfinder",
    "sqlmap",
    "nikto",
    "hydra",
    "medusa",
    "aircrack-ng",
}


@dataclass(frozen=True)
class CommandReview:
    """Result of a command safety review."""

    allowed: bool
    reason: str
    warnings: list[str] = field(default_factory=list)


def review_command(args: list[str]) -> CommandReview:
    """Review a command argument array without executing it.

    The function is intentionally conservative. Future module runners should call
    this before executing any external process.
    """

    if not args:
        return CommandReview(False, "empty command")

    executable = args[0].strip().split("/")[-1].lower()
    joined = " ".join(args).lower()
    warnings: list[str] = []

    if executable in BLOCKED_EXECUTABLES:
        return CommandReview(False, f"blocked executable: {executable}")

    for token in BLOCKED_TOKENS:
        if token in joined:
            return CommandReview(False, f"blocked command pattern: {token}")

    if executable in NETWORK_TOOLS_REQUIRING_REVIEW:
        warnings.append(f"network-capable tool requires explicit authorization: {executable}")

    return CommandReview(True, "command passed basic safety review", warnings)
