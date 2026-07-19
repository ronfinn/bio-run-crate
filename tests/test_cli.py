"""Tests for the Typer CLI."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from bio_run_crate import __version__
from bio_run_crate.cli import app

runner = CliRunner()

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "synthetic"
VALID = EXAMPLES / "valid-run.yaml"
INVALID = EXAMPLES / "invalid-run.yaml"


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_validate_valid_manifest() -> None:
    result = runner.invoke(app, ["validate", str(VALID)])
    assert result.exit_code == 0
    assert "Valid" in result.stdout
    assert "run-001" in result.stdout


def test_validate_invalid_manifest() -> None:
    result = runner.invoke(app, ["validate", str(INVALID)])
    assert result.exit_code == 1


def test_validate_missing_file() -> None:
    result = runner.invoke(app, ["validate", str(EXAMPLES / "nope.yaml")])
    assert result.exit_code == 1
