"""Safety helpers for Open Defense Kit.

This module contains small guardrail utilities that future CLI commands can use
before running any module.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    """Supported module risk levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROHIBITED = "prohibited"


@dataclass(frozen=True)
class ModuleSafetyProfile:
    """Safety metadata required for every Open Defense Kit module."""

    name: str
    category: str
    risk: RiskLevel
    requires_authorization: bool
    network_activity: str
    description: str


def is_allowed_risk(risk: RiskLevel) -> bool:
    """Return True when a module risk level is allowed to run.

    Prohibited modules should never be automated by Open Defense Kit.
    High-risk modules must be lab-only and require extra review before future use.
    """

    return risk in {RiskLevel.LOW, RiskLevel.MEDIUM}


def requires_permission(profile: ModuleSafetyProfile) -> bool:
    """Return whether a module must require explicit permission confirmation."""

    return profile.requires_authorization or profile.risk in {
        RiskLevel.MEDIUM,
        RiskLevel.HIGH,
    }


def permission_statement(target: str) -> str:
    """Generate the confirmation statement users must understand before testing."""

    return (
        "I confirm that I own this target or have explicit written permission "
        f"to test it: {target}"
    )
