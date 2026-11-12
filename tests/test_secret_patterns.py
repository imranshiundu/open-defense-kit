"""Tests for the local secret pattern scanner."""

from pathlib import Path

from odkit.modules.local_secret_patterns import redact, scan_path, should_scan


class TestScanPath:
    def test_detects_aws_access_key(self, tmp_path: Path):
        target = tmp_path / "config.txt"
        target.write_text("aws_key = AKIAABCDEFGHIJKLMNOP\n")
        findings = scan_path(target)
        patterns = {f.pattern for f in findings}
        assert "aws_access_key_like" in patterns

    def test_detects_private_key_marker(self, tmp_path: Path):
        target = tmp_path / "backup.txt"
        target.write_text("-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----\n")
        findings = scan_path(target)
        assert any(f.pattern == "private_key_marker" for f in findings)

    def test_detects_generic_api_key_assignment(self, tmp_path: Path):
        target = tmp_path / "app.py"
        target.write_text('API_KEY = "abcd1234abcd1234abcd"\n')
        findings = scan_path(target)
        assert any(f.pattern == "generic_api_key" for f in findings)

    def test_clean_file_has_no_findings(self, tmp_path: Path):
        target = tmp_path / "clean.py"
        target.write_text("def add(a, b):\n    return a + b\n")
        assert scan_path(target) == []

    def test_short_values_do_not_trigger(self, tmp_path: Path):
        target = tmp_path / "short.py"
        target.write_text("token = 'abc'\n")
        assert scan_path(target) == []

    def test_skips_git_and_node_modules(self, tmp_path: Path):
        hidden = tmp_path / ".git" / "secrets.txt"
        hidden.parent.mkdir()
        hidden.write_text("API_KEY = 'abcd1234abcd1234abcd'\n")
        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "leak.js").write_text("const token = 'abcd1234abcd1234abcd';\n")
        assert scan_path(tmp_path) == []

    def test_scans_recursively(self, tmp_path: Path):
        nested = tmp_path / "src" / "deep"
        nested.mkdir(parents=True)
        (nested / "keys.txt").write_text("aws = AKIAABCDEFGHIJKLMNOP\n")
        findings = scan_path(tmp_path)
        assert len(findings) == 1
        assert "keys.txt" in findings[0].path

    def test_reports_line_numbers(self, tmp_path: Path):
        target = tmp_path / "lines.txt"
        target.write_text("line1\nline2\naws = AKIAABCDEFGHIJKLMNOP\n")
        findings = scan_path(target)
        assert findings[0].line == 3


class TestShouldScan:
    def test_env_files_are_scanned_even_without_suffix(self, tmp_path: Path):
        dot_env = tmp_path / ".env"
        dot_env.write_text("PASSWORD=abcd1234abcd1234abcd\n")
        assert should_scan(dot_env) is True

    def test_binary_suffix_is_skipped(self, tmp_path: Path):
        assert should_scan(tmp_path / "image.png") is False

    def test_directories_are_skipped(self, tmp_path: Path):
        assert should_scan(tmp_path) is False


class TestRedact:
    def test_short_lines_are_kept_intact(self):
        assert redact("short") == "short"

    def test_long_values_are_redacted(self):
        redacted = redact("api_key = 'abcdefghijklmnopqrstuvwxyz0123456789'")
        assert "abcdefghijklmnopqrstuvwxyz" not in redacted
        assert "[redacted]" in redacted
