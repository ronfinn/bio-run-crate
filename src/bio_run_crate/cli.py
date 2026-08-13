"""Command-line interface for bio-run-crate.

The CLI is intentionally thin: it delegates parsing to :mod:`bio_run_crate.manifest`
and rule-based validation to :mod:`bio_run_crate.validation`, and is responsible
only for presentation and exit codes. It contains no validation rules of its own.

Exit codes (see ``docs/architecture.md`` §3.1):

- ``0`` — the manifest parsed and produced no ERROR findings. WARNING and INFO
  findings alone do not change this.
- ``1`` — the manifest parsed, but validation produced at least one ERROR.
- ``2`` — the manifest never reached the rule engine: it was missing or
  unreadable, was not valid YAML, had a non-mapping top level, or failed
  Pydantic's structural/schema validation.
"""

from __future__ import annotations

from pathlib import Path

import typer
import yaml
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from bio_run_crate import __version__
from bio_run_crate.findings import Severity, ValidationResult
from bio_run_crate.manifest import load_manifest
from bio_run_crate.models import RunManifest
from bio_run_crate.validation import validate_manifest

#: Exit code used when a manifest parses but has at least one ERROR finding.
EXIT_VALIDATION_FAILED = 1

#: Exit code used when a manifest cannot be parsed into a model at all.
EXIT_UNUSABLE_MANIFEST = 2

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
    """Parse a run manifest, then check it against the core validation rules.

    Exits 0 if the manifest parsed and produced no ERROR findings, 1 if it
    produced at least one ERROR, and 2 if it could not be parsed into a model at
    all (missing or unreadable file, malformed YAML, non-mapping top level, or a
    structural/schema validation error).
    """
    try:
        run = load_manifest(manifest)
    except ValidationError as error:
        _err.print(f"[bold red]ERROR[/] manifest failed schema validation: {manifest}")
        _render_validation_error(error)
        raise typer.Exit(code=EXIT_UNUSABLE_MANIFEST) from error
    except FileNotFoundError as error:
        _err.print(f"[bold red]ERROR[/] manifest not found: {manifest}")
        raise typer.Exit(code=EXIT_UNUSABLE_MANIFEST) from error
    except (ValueError, yaml.YAMLError, OSError) as error:
        _err.print(f"[bold red]ERROR[/] could not read manifest: {error}")
        raise typer.Exit(code=EXIT_UNUSABLE_MANIFEST) from error

    result = validate_manifest(run)
    if result.findings:
        _render_findings(result)

    _report_summary(run, result)

    if result.has_errors:
        raise typer.Exit(code=EXIT_VALIDATION_FAILED)


#: Colour per severity, for terminal rendering only.
_SEVERITY_STYLE: dict[Severity, str] = {
    Severity.ERROR: "bold red",
    Severity.WARNING: "bold yellow",
    Severity.INFO: "bold blue",
}


def _render_findings(result: ValidationResult) -> None:
    """Render structured findings as a table on stderr, in canonical order."""
    table = Table(title="Validation findings", title_style="bold")
    table.add_column("Rule", style="magenta", no_wrap=True)
    table.add_column("Severity", no_wrap=True)
    table.add_column("Location", style="cyan", no_wrap=True)
    table.add_column("Message", style="white")
    for finding in result.findings:
        style = _SEVERITY_STYLE[finding.severity]
        table.add_row(
            finding.rule_id,
            f"[{style}]{finding.severity}[/]",
            finding.location.path,
            finding.message,
        )
    _err.print(table)


def _report_summary(run: RunManifest, result: ValidationResult) -> None:
    """Print a concise per-run summary on stdout."""
    counts = result.counts()
    if result.has_errors:
        _out.print(f"[bold red]✗ Invalid[/] manifest: [bold]{run.run_id}[/]")
    else:
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
    _out.print(
        f"  findings: {counts[Severity.ERROR]} error(s), "
        f"{counts[Severity.WARNING]} warning(s), "
        f"{counts[Severity.INFO]} info"
    )


def main() -> None:
    """Console-script entry point."""
    app()
