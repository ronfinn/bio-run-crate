"""The JSON validation report: a stable, diffable rendering of one run's findings.

The report exists for automated consumers — CI pipelines, audit tooling,
downstream scripts — which need validation results in a shape they can parse
today and still parse after the tool changes. Its schema is therefore public and
versioned independently of both the package version and the manifest version,
and is documented in ``docs/json-report.md``.

Two steps are kept separate on purpose:

- :func:`build_json_report` turns a parsed manifest and a
  :class:`~bio_run_crate.findings.ValidationResult` into a :class:`JsonReport`,
  the typed in-memory form of the schema.
- :func:`render_json_report` serialises that report to the exact bytes written
  to stdout.

Both are pure functions: no file reads, no network, no rule execution, no
mutation of their inputs, no clock or randomness. Determinism is a contract, not
an accident — see :func:`render_json_report` for how each degree of freedom in
the output is pinned down.

Only findings are reported here. A manifest that never reaches the rule engine —
missing, unreadable, malformed YAML, or structurally invalid — has no
``ValidationResult`` to render, so no report is produced for it; those failures
keep their existing diagnostics and exit code ``2`` (see ``docs/json-report.md``
and ``docs/architecture.md`` §3.1).
"""

from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, Field

from bio_run_crate.findings import Finding, Severity, ValidationResult
from bio_run_crate.models import RunManifest

#: Version of the JSON report *format*.
#:
#: This is not the package version and not ``manifest_version``: it identifies
#: the shape of the document below, so a consumer can branch on it. It changes
#: only when that shape changes incompatibly.
JSON_REPORT_SCHEMA_VERSION = "1"

#: Indentation used when serialising a report. Part of the output contract.
_JSON_INDENT = 2


class SeveritySummary(BaseModel):
    """How many findings of each severity a run produced.

    All three severities are always present, including those with no findings,
    so a consumer can read a count unconditionally rather than treating an
    absent key as zero.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    ERROR: int = Field(ge=0)
    WARNING: int = Field(ge=0)
    INFO: int = Field(ge=0)

    @classmethod
    def from_result(cls, result: ValidationResult) -> "SeveritySummary":
        """Summarise ``result``, without modifying it."""
        counts = result.counts()
        return cls(
            ERROR=counts[Severity.ERROR],
            WARNING=counts[Severity.WARNING],
            INFO=counts[Severity.INFO],
        )


class JsonReport(BaseModel):
    """The public JSON report for one validated run.

    Field declaration order is the key order of the serialised document, so it
    is part of the format rather than an implementation detail. ``findings``
    holds the result's findings exactly as given, which means canonical order —
    :class:`~bio_run_crate.findings.ValidationResult` guarantees that on every
    construction path, so the report never has to sort anything itself.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = Field(default=JSON_REPORT_SCHEMA_VERSION, min_length=1)
    run_id: str = Field(min_length=1)
    summary: SeveritySummary
    findings: tuple[Finding, ...] = ()


def build_json_report(manifest: RunManifest, result: ValidationResult) -> JsonReport:
    """Build the JSON report for ``result`` as produced for ``manifest``.

    A pure function of its two arguments: it performs no I/O, runs no rules and
    mutates neither argument. ``manifest`` is used only to identify the run.

    Args:
        manifest: The manifest that was validated, already parsed.
        result: The findings the validation engine produced for it.
    """
    return JsonReport(
        run_id=manifest.run_id,
        summary=SeveritySummary.from_result(result),
        findings=result.findings,
    )


def render_json_report(report: JsonReport) -> str:
    """Serialise ``report`` to its canonical JSON text.

    Two reports that are semantically identical serialise to byte-identical
    text, so reports can be diffed across runs and machines. Every degree of
    freedom is fixed deliberately:

    - **Key order** follows model field declaration order, top level and nested
      alike. Keys are *not* sorted alphabetically: the declared order reads
      better and is equally stable.
    - **Finding order** is the canonical order already imposed by
      :class:`~bio_run_crate.findings.ValidationResult`, so the order rules ran
      in, or the order a caller supplied findings in, cannot show through.
    - **Formatting** is two-space indentation with no trailing whitespace on any
      line, and the text ends with exactly one newline, so it behaves as a
      well-formed text file under diff.
    - **Content** is plain JSON: severities serialise as their names, and no
      terminal styling can appear because none is ever applied.
    """
    document = report.model_dump(mode="json")
    return (
        json.dumps(
            document,
            indent=_JSON_INDENT,
            ensure_ascii=False,
            sort_keys=False,
            separators=(",", ": "),
        )
        + "\n"
    )
