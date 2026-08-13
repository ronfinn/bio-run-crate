"""Tests for the Typer CLI."""

from __future__ import annotations

import re
from pathlib import Path

from typer.testing import CliRunner

from bio_run_crate import __version__
from bio_run_crate.cli import app

runner = CliRunner()

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "synthetic"
VALID = EXAMPLES / "valid-run.yaml"
INVALID = EXAMPLES / "invalid-run.yaml"
RULE_VIOLATIONS = EXAMPLES / "rule-violations-run.yaml"


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_validate_clean_manifest_exits_zero() -> None:
    """The canonical example has one WARNING (an output without a checksum)."""
    result = runner.invoke(app, ["validate", str(VALID)])
    assert result.exit_code == 0
    assert "Valid" in result.output
    assert "run-001" in result.output


def test_warning_only_manifest_exits_zero_and_reports_the_warning() -> None:
    result = runner.invoke(app, ["validate", str(VALID)])
    assert result.exit_code == 0
    assert "CORE-003" in result.output
    assert "WARNING" in result.output
    assert "1 warning(s)" in result.output


def test_validate_manifest_with_error_finding_exits_one() -> None:
    result = runner.invoke(app, ["validate", str(RULE_VIOLATIONS)])
    assert result.exit_code == 1
    assert "Invalid" in result.output


def test_finding_output_shows_rule_id_severity_location_and_message() -> None:
    result = runner.invoke(app, ["validate", str(RULE_VIOLATIONS)])
    # The table wraps long messages across rows; strip its borders and collapse
    # layout whitespace so a full sentence can be matched.
    rendered = re.sub(r"\s+", " ", re.sub(r"[│┃]", " ", result.output))
    assert "CORE-001" in rendered
    assert "ERROR" in rendered
    assert "inputs[1].id" in rendered
    assert "must be unique within their collection" in rendered


def test_schema_invalid_manifest_exits_two() -> None:
    result = runner.invoke(app, ["validate", str(INVALID)])
    assert result.exit_code == 2


def test_missing_file_exits_two() -> None:
    result = runner.invoke(app, ["validate", str(EXAMPLES / "nope.yaml")])
    assert result.exit_code == 2


def test_malformed_yaml_exits_two(tmp_path: Path) -> None:
    manifest = tmp_path / "malformed.yaml"
    manifest.write_text("run_id: run-001\n  bad indentation:\n", encoding="utf-8")
    result = runner.invoke(app, ["validate", str(manifest)])
    assert result.exit_code == 2


def test_non_mapping_yaml_exits_two(tmp_path: Path) -> None:
    manifest = tmp_path / "sequence.yaml"
    manifest.write_text("- run-001\n- run-002\n", encoding="utf-8")
    result = runner.invoke(app, ["validate", str(manifest)])
    assert result.exit_code == 2


def test_unreadable_file_exits_two(tmp_path: Path) -> None:
    manifest = tmp_path / "unreadable.yaml"
    manifest.write_text("run_id: run-001\n", encoding="utf-8")
    manifest.chmod(0o000)
    try:
        result = runner.invoke(app, ["validate", str(manifest)])
    finally:
        manifest.chmod(0o600)
    assert result.exit_code == 2
