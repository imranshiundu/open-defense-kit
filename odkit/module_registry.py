"""Safe module registry for Open Defense Kit."""

from __future__ import annotations

from dataclasses import dataclass

from odkit.safety import ModuleSafetyProfile, RiskLevel


@dataclass(frozen=True)
class ModuleDefinition:
    """A documented Open Defense Kit module."""

    slug: str
    safety: ModuleSafetyProfile
    docs: str
    enabled: bool = True


MODULES: dict[str, ModuleDefinition] = {
    "local-secret-patterns": ModuleDefinition(
        slug="local-secret-patterns",
        safety=ModuleSafetyProfile(
            name="Local Secret Pattern Review",
            category="code-security",
            risk=RiskLevel.LOW,
            requires_authorization=False,
            network_activity="none",
            description="Find common secret-like patterns in local text files without network access.",
        ),
        docs="docs/modules/local-secret-patterns.md",
    ),
    "security-headers-notes": ModuleDefinition(
        slug="security-headers-notes",
        safety=ModuleSafetyProfile(
            name="Security Headers Notes",
            category="web-security-education",
            risk=RiskLevel.LOW,
            requires_authorization=False,
            network_activity="none",
            description="Educational checklist for common defensive HTTP security headers.",
        ),
        docs="docs/modules/security-headers-notes.md",
    ),
}


def list_modules() -> list[ModuleDefinition]:
    """Return all known modules."""

    return list(MODULES.values())


def get_module(slug: str) -> ModuleDefinition | None:
    """Return one module by slug."""

    return MODULES.get(slug)
