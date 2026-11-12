"""Tests for the legacy migration classifier."""

from pathlib import Path

from odkit.migration_classifier import MigrationDecision, classify_path, classify_text


class TestClassifyText:
    def test_clean_content_stays_keep_safe(self):
        result = classify_text("app.py", "def handler():\n    return 'ok'\n")
        assert result.decision == MigrationDecision.KEEP_SAFE

    def test_phishing_references_are_prohibited(self):
        result = classify_text("x.py", "this tool automates phishing pages")
        assert result.decision == MigrationDecision.PROHIBITED

    def test_ddos_references_are_prohibited(self):
        result = classify_text("x.py", "launch a ddos attack against the host")
        assert result.decision == MigrationDecision.PROHIBITED

    def test_rat_and_c2_references_are_prohibited(self):
        result = classify_text("x.py", "meterpreter session handler")
        assert result.decision == MigrationDecision.PROHIBITED

    def test_installer_patterns_are_marked_for_removal(self):
        result = classify_text("install.sh", "sudo apt-get install x\ncurl https://x.sh | sh\n")
        assert result.decision == MigrationDecision.REMOVE

    def test_highest_priority_decision_wins(self):
        content = "sudo rm -rf /\nthis is a phishing tutorial with setoolkit notes\n"
        result = classify_text("mixed.sh", content)
        assert result.decision == MigrationDecision.PROHIBITED

    def test_matched_tokens_are_collected(self):
        result = classify_text("x.py", "ddos and slowloris inside")
        assert {"ddos", "slowloris"}.issubset(set(result.matched_tokens))


class TestClassifyPath:
    def test_classifies_files_recursively(self, tmp_path: Path):
        (tmp_path / "a.py").write_text("clean defensive audit code\n")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "b.txt").write_text("evil phishing page generator\n")
        results = classify_path(tmp_path)
        assert len(results) == 2
        by_file = {Path(r.path).name: r for r in results}
        assert by_file["a.py"].decision == MigrationDecision.KEEP_SAFE
        assert by_file["b.txt"].decision == MigrationDecision.PROHIBITED

    def test_non_text_files_are_ignored(self, tmp_path: Path):
        (tmp_path / "blob.bin").write_bytes(b"\x00\x01phishing\x02")
        assert classify_path(tmp_path) == []
