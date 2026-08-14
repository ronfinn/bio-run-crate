"""Rendering of validation results into report formats.

Reporters are the last stage of the pipeline described in
``docs/architecture.md`` §3.5: a manifest is parsed into a
:class:`~bio_run_crate.models.RunManifest`, the validation engine turns that into
a :class:`~bio_run_crate.findings.ValidationResult`, and a reporter renders the
two into an output format. A reporter is a *pure consumer* of those two values —
it never re-reads the manifest, re-runs validation, mutates its inputs, touches
the network or the clock, or emits terminal styling.

Today this package provides the JSON report
(:mod:`bio_run_crate.reporting.json_report`), whose schema is documented in
``docs/json-report.md``. The Markdown report is issue #8 and is not implemented.
"""

from __future__ import annotations

from bio_run_crate.reporting.json_report import (
    JSON_REPORT_SCHEMA_VERSION,
    JsonReport,
    SeveritySummary,
    build_json_report,
    render_json_report,
)

__all__ = [
    "JSON_REPORT_SCHEMA_VERSION",
    "JsonReport",
    "SeveritySummary",
    "build_json_report",
    "render_json_report",
]
