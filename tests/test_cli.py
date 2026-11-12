"""CLI integration tests: every command runs end-to-end via main()."""

import json
from pathlib import Path

import pytest

from odkit.cli import main


@pytest.fixture()
def risky_tree(tmp_path: Path) -> Path:
    (tmp_path / "app.py").write_text('API_KEY = "abcd1234abcd1234abcd"\n')
    return tmp_path


class TestSimpleCommands:
    def test_doctor_reports_scaffold_status(self, capsys):
        assert main(["doctor"]) == 0
        out = capsys.readouterr().out
        assert "Open Defense Kit" in out
        assert "Root required: no" in out

    def test_safety_prints_prohibited_rules(self, capsys):
        assert main(["safety"]) == 0
        out = capsys.readouterr().out
        assert "Prohibited" in out
        assert "phishing" in out

    def test_permission_statement(self, capsys):
        assert main(["permission", "lab.local"]) == 0
        assert "lab.local" in capsys.readouterr().out

    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0
        assert "2.1.0" in capsys.readouterr().out

    def test_help_mentions_audit_report(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0
        assert "audit-report" in capsys.readouterr().out


class TestModulesCommand:
    def test_modules_list_includes_audit_report(self, capsys):
        assert main(["modules", "list"]) == 0
        out = capsys.readouterr().out
        assert "local-secret-patterns" in out
        assert "audit-report" in out

    def test_modules_info_shows_safety_profile(self, capsys):
        assert main(["modules", "info", "audit-report"]) == 0
        out = capsys.readouterr().out
        assert "Risk: low" in out
        assert "Network activity: none" in out

    def test_modules_info_unknown_slug_fails(self, capsys):
        assert main(["modules", "info", "nope"]) == 1


class TestScanAndAudit:
    def test_scan_secrets_finds_issues(self, risky_tree, capsys):
        exit_code = main(["scan-secrets", str(risky_tree)])
        assert exit_code == 2
        assert "generic_api_key" in capsys.readouterr().out

    def test_scan_secrets_clean_tree(self, tmp_path, capsys):
        (tmp_path / "clean.py").write_text("print('hello')\n")
        assert main(["scan-secrets", str(tmp_path)]) == 0

    def test_missing_path_is_reported(self, capsys):
        assert main(["scan-secrets", "/no/such/path"]) == 1


class TestAuditReportCommand:
    def test_writes_html_json_and_markdown(self, risky_tree, tmp_path):
        html_out = tmp_path / "report.html"
        json_out = tmp_path / "report.json"
        md_out = tmp_path / "report.md"

        exit_code = main([
            "audit-report", str(risky_tree),
            "--html", str(html_out),
            "--json", str(json_out),
            "--markdown", str(md_out),
        ])
        assert exit_code == 2  # findings exist

        assert html_out.exists() and html_out.stat().st_size > 1000
        assert json_out.exists() and md_out.exists()

        payload = json.loads(json_out.read_text())
        assert payload["module"] == "audit-report"
        assert payload["total_findings"] > 0

    def test_console_summary_without_flags(self, risky_tree, capsys):
        exit_code = main(["audit-report", str(risky_tree)])
        assert exit_code == 2
        out = capsys.readouterr().out
        assert "Grade:" in out
        assert "CRITICAL" in out

    def test_clean_target_exits_zero(self, tmp_path):
        (tmp_path / "readme.md").write_text("just docs\n")
        assert main(["audit-report", str(tmp_path)]) == 0

    def test_missing_target_exits_one(self, capsys):
        assert main(["audit-report", "/no/such/path"]) == 1

    def test_stdout_json_output(self, risky_tree, capsys):
        main(["audit-report", str(risky_tree), "--stdout", "json"])
        payload = json.loads(capsys.readouterr().out)
        assert payload["module"] == "audit-report"
