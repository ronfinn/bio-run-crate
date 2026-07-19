"""Command-line interface for bio-run-crate.

The CLI is intentionally thin: it delegates parsing to :mod:`bio_run_crate.manifest`
and validation to the models, and is responsible only for presentation and exit
codes. Every failure mode exits with code 1; a valid manifest exits with 0.
"""

from __future__ import annotations

from pathlib import Path

import typer
import yaml
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from bio_run_crate import __version__
from bio_run_crate.manifest import load_manifest
from bio_run_crate.models import RunManifest

app = typer.Typer(
    help="Validate biological analysis-run metadata and build RO-Crates.",
    no_args_is_help=True,
)

# Findings/errors go to stderr so success output on stdout stays machine-clean.
_out = Console()
_err = Console(stderr=True)


@app.command()
def version() -> None:
    """Print the installed version and exit."""
    typer.echo(__version__)


def _render_validation_error(error: ValidationError) -> None:
    """Render Pydantic errors as a readable table on stderr."""
    table = Table(title="Manifest validation errors", title_style="bold red")
    table.add_column("Location", style="cyan", no_wrap=True)
    table.add_column("Problem", style="white")
    table.add_column("Type", style="dim")
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"]) or "(root)"
        table.add_row(location, item["msg"], str(item["type"]))
    _err.print(table)


@app.command()
def validate(
    manifest: Path = typer.Argument(
        ...,
        dir_okay=False,
        help="Path to a YAML run manifest.",
    ),
) -> None:
    """Parse and validate a run manifest against the RunManifest model.

    Exits 0 if the manifest is valid, 1 for any failure (missing or unreadable
    file, malformed YAML, non-mapping top level, or a validation error).
    """
    try:
        run = load_manifest(manifest)
    except ValidationError as error:
        _err.print(f"[bold red]ERROR[/] manifest failed validation: {manifest}")
        _render_validation_error(error)
        raise typer.Exit(code=1) from error
    except FileNotFoundError as error:
        _err.print(f"[bold red]ERROR[/] manifest not found: {manifest}")
        raise typer.Exit(code=1) from error
    except (ValueError, yaml.YAMLError, OSError) as error:
        _err.print(f"[bold red]ERROR[/] could not read manifest: {error}")
        raise typer.Exit(code=1) from error

    _report_success(run)


def _report_success(run: RunManifest) -> None:
    """Print a concise success summary on stdout."""
    _out.print(f"[bold green]✓ Valid[/] manifest: [bold]{run.run_id}[/]")
    _out.print(
        f"  project [cyan]{run.project.id}[/] · "
        f"dataset [cyan]{run.dataset.id}[/] · "
        f"organism [italic]{run.biological_context.organism.scientific_name}[/]"
    )
    _out.print(
        f"  assay [cyan]{run.assay.type}[/] · "
        f"workflow [cyan]{run.workflow.name} {run.workflow.version}[/] · "
        f"{len(run.inputs)} input(s), {len(run.outputs)} output(s)"
    )


def main() -> None:
    """Console-script entry point."""
    app()
