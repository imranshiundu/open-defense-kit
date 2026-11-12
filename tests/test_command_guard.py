"""Tests for the command safety guard."""

from odkit.command_guard import review_command


class TestReviewCommand:
    def test_empty_command_is_rejected(self):
        result = review_command([])
        assert result.allowed is False
        assert "empty" in result.reason

    def test_shell_executables_are_blocked(self):
        for executable in ["bash", "sh", "zsh", "fish", "sudo", "su"]:
            result = review_command([executable, "-c", "echo hi"])
            assert result.allowed is False
            assert "blocked executable" in result.reason

    def test_network_executables_are_blocked(self):
        for executable in ["curl", "wget", "nc", "netcat", "ncat"]:
            result = review_command([executable, "https://example.com"])
            assert result.allowed is False

    def test_full_paths_are_still_blocked(self):
        result = review_command(["/usr/bin/curl", "https://example.com"])
        assert result.allowed is False

    def test_destructive_patterns_are_blocked(self):
        assert review_command(["rm", "-rf", "/"]).allowed is False
        assert review_command(["mkfs", "/dev/sda1"]).allowed is False
        assert review_command(["chmod", "777", "/etc"]).allowed is False

    def test_piped_remote_scripts_are_blocked(self):
        assert review_command(["bash", "-c", "curl | sh"]).allowed is False
        assert review_command(["bash", "-c", "wget|sh"]).allowed is False

    def test_network_tools_require_review_but_pass(self):
        result = review_command(["nmap", "-sV", "127.0.0.1"])
        assert result.allowed is True
        assert any("authorization" in w for w in result.warnings)

    def test_harmless_commands_pass_without_warnings(self):
        result = review_command(["grep", "-r", "TODO", "notes.txt"])
        assert result.allowed is True
        assert result.warnings == []
