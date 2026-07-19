"""Command-line interface for bio-run-crate.

The CLI is intentionally thin: it delegates parsing to :mod:`bio_run_crate.manifest`
and validation to the models, and is responsible only for presentation and exit
codes.
"""

from __future__ import annotations

from pathlib import Path

import typer
import yaml
from pydantic import ValidationError

from bio_run_crate import __version__
from bio_run_crate.manifest import load_manifest

app = typer.Typer(
    help="Validate biological analysis-run metadata and build RO-Crates.",
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Print the installed version and exit."""
    typer.echo(__version__)


@app.command()
def validate(
    manifest: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to a YAML run manifest.",
    ),
) -> None:
    """Parse and validate a run manifest against the RunManifest model."""
    try:
        load_manifest(manifest)
    except ValidationError as error:
        typer.echo("ERROR: manifest failed validation:", err=True)
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error
    except (ValueError, yaml.YAMLError, OSError) as error:
        typer.echo(f"ERROR: could not read manifest: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo("OK: manifest parsed and validated (RunManifest)")


def main() -> None:
    """Console-script entry point."""
    app()
