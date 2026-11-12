"""Tests for the audit report generator."""

import json
import os
from pathlib import Path

import pytest

from odkit.report import build_report, report_to_html, report_to_json, report_to_markdown


@pytest.fixture()
def risky_tree(tmp_path: Path) -> Path:
    """A small tree that triggers every scanner category."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(
        'API_KEY = "abcd1234abcd1234abcd"\n'
    )
    (tmp_path / "src" / "keys.txt").write_text(
        "aws = AKIAABCDEFGHIJKLMNOP\n"
    )
    (tmp_path / "src" / "backup.txt").write_text(
        "-----BEGIN RSA PRIVATE KEY-----\nMIIB\n-----END RSA PRIVATE KEY-----\n"
    )
    (tmp_path / "deploy.sh").write_text(
        "# legacy deploy\ncurl https://get.example.sh | sh\n"
    )
    (tmp_path / ".env").write_text("PASSWORD=supersecretvalue12345\n")
    world_writable = tmp_path / "shared.conf"
    world_writable.write_text("debug = true\n")
    os.chmod(world_writable, 0o666)
    return tmp_path


class TestBuildReport:
    def test_clean_tree_scores_grade_a(self, tmp_path: Path):
        report = build_report(str(tmp_path))
        assert report.total_findings == 0
        assert report.grade == "A"
        assert all(count == 0 for count in report.severity_counts.values())

    def test_detects_secrets_with_severities(self, risky_tree: Path):
        report = build_report(str(risky_tree))
        assert report.severity_counts["CRITICAL"] >= 2  # AWS key + private key
        assert report.severity_counts["HIGH"] >= 1  # generic api key

    def test_detects_legacy_risky_patterns(self, risky_tree: Path):
        report = build_report(str(risky_tree))
        assert any(f.category == "remote_script" for f in report.legacy_findings)

    def test_detects_hygiene_problems(self, risky_tree: Path):
        kinds = {f.kind for f in report_hygiene(risky_tree)}
        assert "credential_file_present" in kinds
        assert "world_writable_file" in kinds

    def test_risky_tree_never_gets_grade_a(self, risky_tree: Path):
        assert build_report(str(risky_tree)).grade in {"B", "C", "D", "F"}

    def test_missing_target_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            build_report(str(tmp_path / "does-not-exist"))

    def test_scan_metadata_is_present(self, risky_tree: Path):
        report = build_report(str(risky_tree))
        assert report.scan_id
        assert "UTC" in report.generated_at
        assert report.files_scanned > 0

    def test_exclude_drops_fixture_findings(self, risky_tree: Path):
        (risky_tree / "tests").mkdir()
        (risky_tree / "tests" / "fixture.py").write_text('PASSWORD = "abcd1234abcd1234abcd"\n')
        full = build_report(str(risky_tree))
        filtered = build_report(str(risky_tree), exclude={"tests"})
        assert filtered.total_findings < full.total_findings
        assert all("tests" not in Path(f.path).parts for f in filtered.secret_findings)
        assert all("tests" not in Path(f.path).parts for f in filtered.legacy_findings)
        assert all("tests" not in Path(f.path).parts for f in filtered.hygiene_findings)


def report_hygiene(root: Path):
    return build_report(str(root)).hygiene_findings


class TestRenderers:
    def test_json_is_valid_and_complete(self, risky_tree: Path):
        report = build_report(str(risky_tree))
        payload = json.loads(report_to_json(report))
        assert payload["module"] == "audit-report"
        assert payload["grade"] == report.grade
        assert payload["total_findings"] == report.total_findings
        assert payload["secrets"] and payload["hygiene"]
        assert payload["recommendations"]
        assert "disclaimer" in payload

    def test_markdown_renders_tables_and_recommendations(self, risky_tree: Path):
        report = build_report(str(risky_tree))
        markdown = report_to_markdown(report)
        assert "# ODK Security Audit Report" in markdown
        assert "## Recommendations" in markdown
        assert "`CRITICAL`" in markdown or "CRITICAL" in markdown

    def test_html_is_self_contained(self, risky_tree: Path):
        report = build_report(str(risky_tree))
        html = report_to_html(report)
        assert "<!DOCTYPE html>" in html
        assert "Open Defense Kit" in html
        assert esc(report.target) in html
        # No external asset references: the report must work fully offline.
        assert 'src="http' not in html
        assert 'href="http' not in html

    def test_html_escapes_finding_previews(self, tmp_path: Path):
        evil = tmp_path / "evil.txt"
        evil.write_text("<script>alert('xss')</script> password=abcd1234abcd1234abcd\n")
        html = report_to_html(build_report(str(tmp_path)))
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html


def esc(text: str) -> str:
    from html import escape

    return escape(str(text))
