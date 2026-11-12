"""Tests for the safety guardrails."""

from odkit.safety import (
    ModuleSafetyProfile,
    RiskLevel,
    is_allowed_risk,
    permission_statement,
    requires_permission,
)


class TestRiskLevels:
    def test_low_and_medium_risks_are_allowed(self):
        assert is_allowed_risk(RiskLevel.LOW) is True
        assert is_allowed_risk(RiskLevel.MEDIUM) is True

    def test_high_risk_is_lab_only(self):
        assert is_allowed_risk(RiskLevel.HIGH) is False

    def test_prohibited_risk_is_never_automated(self):
        assert is_allowed_risk(RiskLevel.PROHIBITED) is False


class TestPermissionGates:
    def test_low_risk_local_module_needs_no_permission(self):
        profile = ModuleSafetyProfile(
            name="Local scan",
            category="code-security",
            risk=RiskLevel.LOW,
            requires_authorization=False,
            network_activity="none",
            description="local only",
        )
        assert requires_permission(profile) is False

    def test_medium_risk_requires_permission_even_if_not_marked(self):
        profile = ModuleSafetyProfile(
            name="Network scan",
            category="network",
            risk=RiskLevel.MEDIUM,
            requires_authorization=False,
            network_activity="direct",
            description="touches the network",
        )
        assert requires_permission(profile) is True

    def test_explicit_authorization_flag_always_requires_permission(self):
        profile = ModuleSafetyProfile(
            name="Sensitive scan",
            category="audit",
            risk=RiskLevel.LOW,
            requires_authorization=True,
            network_activity="none",
            description="reads user files",
        )
        assert requires_permission(profile) is True


class TestPermissionStatement:
    def test_statement_mentions_ownership_and_target(self):
        statement = permission_statement("10.0.0.5")
        assert "own this target" in statement
        assert "written permission" in statement
        assert "10.0.0.5" in statement
