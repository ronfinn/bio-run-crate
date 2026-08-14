"""Tests for the Typer CLI."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from bio_run_crate import __version__
from bio_run_crate.cli import app

runner = CliRunner()

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "synthetic"
VALID = EXAMPLES / "valid-run.yaml"
INVALID = EXAMPLES / "invalid-run.yaml"
RULE_VIOLATIONS = EXAMPLES / "rule-violations-run.yaml"
MISSING_REQUIRED_FIELD = EXAMPLES / "missing-required-field-run.yaml"
WRONG_FIELD_TYPE = EXAMPLES / "wrong-field-type-run.yaml"
DUPLICATE_OUTPUT_ID = EXAMPLES / "duplicate-output-id-run.yaml"


def _flatten(output: str) -> str:
    """Strip table borders and collapse whitespace so sentences can be matched."""
    return re.sub(r"\s+", " ", re.sub(r"[│┃]", " ", output))


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
    rendered = _flatten(result.output)
    assert "CORE-001" in rendered
    assert "ERROR" in rendered
    assert "inputs[1].id" in rendered
    assert "must be unique within their collection" in rendered


def test_schema_invalid_manifest_exits_two() -> None:
    result = runner.invoke(app, ["validate", str(INVALID)])
    assert result.exit_code == 2


def test_missing_required_field_fixture_exits_two_and_names_the_field() -> None:
    """`missing-required-field-run.yaml` omits `workflow.version` only."""
    result = runner.invoke(app, ["validate", str(MISSING_REQUIRED_FIELD)])
    rendered = _flatten(result.output)
    assert result.exit_code == 2
    assert "workflow.version" in rendered
    assert "missing" in rendered
    # A structural failure stops before the rule engine, so no finding is shown.
    assert "CORE-" not in rendered


def test_wrong_field_type_fixture_exits_two_and_names_the_field() -> None:
    """`wrong-field-type-run.yaml` gives `inputs` as a scalar, not a list."""
    result = runner.invoke(app, ["validate", str(WRONG_FIELD_TYPE)])
    rendered = _flatten(result.output)
    assert result.exit_code == 2
    assert "list_type" in rendered
    assert "should be a valid list" in rendered
    assert "CORE-" not in rendered


def test_duplicate_output_id_fixture_exits_one_with_only_core_001() -> None:
    """`duplicate-output-id-run.yaml` reuses `output-001` and nothing else."""
    result = runner.invoke(app, ["validate", str(DUPLICATE_OUTPUT_ID)])
    rendered = _flatten(result.output)
    assert result.exit_code == 1
    assert "CORE-001" in rendered
    assert "ERROR" in rendered
    assert "outputs[1].id" in rendered
    assert "1 error(s), 0 warning(s), 0 info" in rendered


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


def test_text_format_is_the_default_and_is_explicitly_selectable() -> None:
    """`--format text` must be exactly today's behaviour, not a variant of it."""
    default = runner.invoke(app, ["validate", str(VALID)])
    explicit = runner.invoke(app, ["validate", str(VALID), "--format", "text"])
    assert explicit.exit_code == default.exit_code == 0
    assert explicit.output == default.output
    assert "{" not in explicit.stdout


def _json_stdout(result: Any) -> dict[str, Any]:
    """Parse a `--format json` run's stdout, asserting it is a lone JSON document."""
    document: dict[str, Any] = json.loads(result.stdout)
    return document


def test_json_format_on_a_warning_only_manifest_exits_zero_with_one_warning() -> None:
    result = runner.invoke(app, ["validate", str(VALID), "--format", "json"])
    assert result.exit_code == 0
    document = _json_stdout(result)
    assert document["schema_version"] == "1"
    assert document["run_id"] == "run-001"
    assert document["summary"] == {"ERROR": 0, "WARNING": 1, "INFO": 0}
    assert document["findings"][0]["rule_id"] == "CORE-003"
    assert document["findings"][0]["severity"] == "WARNING"


def test_json_stdout_carries_no_table_summary_or_ansi_styling() -> None:
    result = runner.invoke(app, ["validate", str(VALID), "--format", "json"])
    stdout = result.stdout
    assert stdout.endswith("}\n")
    # Nothing from the human-facing presentation may leak into the document.
    assert "Valid" not in stdout
    assert "findings:" not in stdout
    assert "\x1b[" not in stdout
    assert not any(border in stdout for border in "│┃─┌╭")


def test_json_format_on_an_error_manifest_exits_one_and_still_reports() -> None:
    result = runner.invoke(app, ["validate", str(DUPLICATE_OUTPUT_ID), "-f", "json"])
    assert result.exit_code == 1
    document = _json_stdout(result)
    assert document["summary"] == {"ERROR": 1, "WARNING": 0, "INFO": 0}
    (finding,) = document["findings"]
    assert finding["rule_id"] == "CORE-001"
    assert finding["location"] == {"path": "outputs[1].id"}


def test_json_format_is_byte_identical_across_runs() -> None:
    first = runner.invoke(app, ["validate", str(RULE_VIOLATIONS), "--format", "json"])
    second = runner.invoke(app, ["validate", str(RULE_VIOLATIONS), "--format", "json"])
    assert first.stdout == second.stdout


def test_structural_failure_in_json_mode_exits_two_without_a_report() -> None:
    """No `RunManifest` means no findings, so there is nothing to report."""
    result = runner.invoke(
        app, ["validate", str(MISSING_REQUIRED_FIELD), "--format", "json"]
    )
    assert result.exit_code == 2
    assert result.stdout == ""
    # The existing schema diagnostic is unchanged.
    rendered = _flatten(result.output)
    assert "workflow.version" in rendered
    assert "missing" in rendered


def test_unknown_format_value_is_rejected_by_typer() -> None:
    result = runner.invoke(app, ["validate", str(VALID), "--format", "yaml"])
    assert result.exit_code != 0
    assert "yaml" in _flatten(result.output)
    assert result.stdout == ""


def test_unreadable_file_exits_two(tmp_path: Path) -> None:
    manifest = tmp_path / "unreadable.yaml"
    manifest.write_text("run_id: run-001\n", encoding="utf-8")
    manifest.chmod(0o000)
    try:
        result = runner.invoke(app, ["validate", str(manifest)])
    finally:
        manifest.chmod(0o600)
    assert result.exit_code == 2
