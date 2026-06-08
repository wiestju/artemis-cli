"""
Unit tests — no network, no credentials required.

These run in CI against every Python version to ensure the CLI
is importable, all commands are registered, and core utilities
behave correctly.
"""
import json
import pytest
from click.testing import CliRunner
from artemis_cli.cli.main import cli
from artemis_cli.cli.assess import _load_feedbacks


# ---------------------------------------------------------------------------
# CLI structure — all top-level commands and groups must be reachable
# ---------------------------------------------------------------------------

class TestHelp:
    def setup_method(self):
        self.runner = CliRunner()

    def _ok(self, *args):
        result = self.runner.invoke(cli, list(args) + ["--help"])
        assert result.exit_code == 0, result.output
        return result.output

    def test_root_help(self):
        assert "artemis" in self._ok().lower()

    def test_login_help(self):
        out = self._ok("login")
        assert "--server" in out

    def test_courses_help(self):
        self._ok("courses")

    def test_courses_list_help(self):
        out = self._ok("courses", "list")
        assert "courses" in out.lower() or "list" in out.lower()

    def test_courses_exercises_help(self):
        self._ok("courses", "exercises")

    def test_exercises_help(self):
        self._ok("exercises")

    def test_exercises_view_help(self):
        self._ok("exercises", "view")

    def test_exercises_dashboard_help(self):
        self._ok("exercises", "dashboard")

    def test_exercises_next_help(self):
        out = self._ok("exercises", "next")
        assert "--correction-round" in out

    def test_exercises_submissions_help(self):
        self._ok("exercises", "submissions")

    def test_submissions_help(self):
        self._ok("submissions")

    def test_submissions_view_help(self):
        self._ok("submissions", "view")

    def test_submissions_result_help(self):
        self._ok("submissions", "result")

    def test_submissions_download_help(self):
        out = self._ok("submissions", "download")
        assert "--output" in out

    def test_assess_help(self):
        self._ok("assess")

    def test_assess_interactive_help(self):
        self._ok("assess", "interactive")

    def test_assess_submit_help(self):
        out = self._ok("assess", "submit")
        assert "--feedbacks" in out

    def test_assess_cancel_help(self):
        self._ok("assess", "cancel")

    def test_assess_external_help(self):
        out = self._ok("assess", "external")
        assert "--student" in out

    def test_complaints_help(self):
        self._ok("complaints")

    def test_complaints_list_help(self):
        self._ok("complaints", "list")

    def test_complaints_respond_help(self):
        self._ok("complaints", "respond")


# ---------------------------------------------------------------------------
# _load_feedbacks — JSON parsing utility
# ---------------------------------------------------------------------------

class TestLoadFeedbacks:
    def test_none_returns_empty(self):
        assert _load_feedbacks(None) == []

    def test_empty_string_returns_empty(self):
        assert _load_feedbacks("") == []

    def test_inline_json_array(self):
        fb = [{"text": "Good", "credits": 3.0, "type": "MANUAL_UNREFERENCED"}]
        result = _load_feedbacks(json.dumps(fb))
        assert result == fb

    def test_inline_json_empty_array(self):
        assert _load_feedbacks("[]") == []

    def test_file_path(self, tmp_path):
        fb = [{"text": "Test feedback", "credits": -1.0, "type": "MANUAL_UNREFERENCED"}]
        p = tmp_path / "feedbacks.json"
        p.write_text(json.dumps(fb))
        result = _load_feedbacks(str(p))
        assert result == fb

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            _load_feedbacks("{not valid json")


# ---------------------------------------------------------------------------
# assess submit — rejects bad feedback JSON with exit code 1
# ---------------------------------------------------------------------------

class TestAssessSubmitValidation:
    def setup_method(self):
        self.runner = CliRunner()

    def test_bad_feedbacks_json_exits_nonzero(self):
        result = self.runner.invoke(
            cli,
            ["assess", "submit", "999", "--feedbacks", "{bad json}"],
        )
        assert result.exit_code != 0
