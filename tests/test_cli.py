"""Tests for the Typer CLI."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from bio_run_crate import __version__
from bio_run_crate.cli import app

runner = CliRunner()

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "run_manifest.yaml"


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_validate_valid_manifest() -> None:
    result = runner.invoke(app, ["validate", str(EXAMPLE)])
    assert result.exit_code == 0
    assert "OK: manifest parsed and validated" in result.stdout


def test_validate_invalid_manifest(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("schema_version: '0.1'\ntitle: missing fields\n", encoding="utf-8")
    result = runner.invoke(app, ["validate", str(bad)])
    assert result.exit_code == 1
