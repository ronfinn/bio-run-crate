# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
While the project is pre-1.0 (`0.x`), minor versions may include breaking
changes.

## [Unreleased]

### Added

- JSON validation report in a new `bio_run_crate.reporting` package: a versioned
  (`schema_version`, currently `"1"`), documented document carrying the run
  identifier, a per-severity summary that always includes all three severities
  even when zero, and every finding with its rule ID, severity, message and
  structured `location`. `build_json_report()` and `render_json_report()` are
  pure functions of an already-parsed manifest and a `ValidationResult` — no file
  reads, no network, no rule execution, no mutation, no clock or randomness.
  Serialization is deterministic by contract: fixed key order, canonical finding
  order, fixed indentation and exactly one trailing newline, so two reports for
  the same result are byte-identical and diffable. The full schema is documented
  in `docs/json-report.md`.
- `validate --format {text,json}` (`-f`), an enumeration rather than a `--json`
  flag so further formats can be added as members. `text` is the default and
  unchanged. `json` writes exactly one report to stdout and suppresses the
  findings table and human summary, with no Rich styling; exit codes are
  unchanged, so a WARNING-only run emits a full report and still exits `0`. A
  manifest that fails structurally never reaches the rule engine, so it produces
  no report — its existing diagnostics stay on stderr and it still exits `2`.
- Core validation engine in `bio_run_crate.validation`: a `Rule` abstraction
  (stable rule ID, declared severity, description, and a pure check over a
  parsed manifest), a `RuleRegistry` that enforces rule-ID uniqueness and
  can pin the namespace its rules must use and refuses to reuse an explicitly
  retired identifier, the modality-agnostic core rule set, and
  `validate_manifest()`, which applies a rule set to a manifest and returns a
  `ValidationResult`. Validation is offline, deterministic, runs every rule
  rather than stopping at the first, and never mutates the manifest.
- Core rules `CORE-001` (a resource `id` used more than once within `inputs` or
  `outputs` — ERROR) and `CORE-003` (an output with no checksum — WARNING),
  documented in `docs/data-model.md` §A.8.2. The set is deliberately minimal:
  a rule ships only where the data model already states the invariant it checks.
  Each rule declares exactly one severity, which the engine enforces.
- An explicit uniqueness contract for resource identifiers in
  `docs/data-model.md` §A.7: an `id` must be unique within its collection. This
  is a cross-field invariant that per-field schema validation cannot express,
  and is what `CORE-001` enforces.
- `validate` now runs the core rules after schema validation and renders the
  resulting findings — rule ID, severity, location and message — as a table on
  stderr, with a per-severity count in the stdout summary.
- Three narrowly targeted synthetic examples, each isolating one failure so its
  diagnostic can be studied on its own:
  `examples/synthetic/missing-required-field-run.yaml` (a required field is
  missing — exit `2`), `examples/synthetic/wrong-field-type-run.yaml` (a field
  has the wrong type — exit `2`) and
  `examples/synthetic/duplicate-output-id-run.yaml` (schema-valid but breaks
  `CORE-001` — exit `1`). The example library is tabulated in the README and in
  `docs/data-model.md` Part C.
- A third synthetic example, `examples/synthetic/rule-violations-run.yaml`: a
  schema-valid manifest that deliberately violates core rules.
- Structured validation findings in `bio_run_crate.findings`: a `Severity`
  enumeration limited to `ERROR`, `WARNING` and `INFO`; a frozen `Finding`
  model carrying a stable rule identifier, severity, message and a `Location`
  into the manifest; and a `ValidationResult` container that holds its findings
  in a canonical, deterministic order on every construction path. Both models
  are JSON-serialisable. The rule-ID syntax (`<NAMESPACE>-<NNN>`, core rules
  under `CORE`) is documented in `docs/data-model.md` §A.8.1 and validated by the
  model; uniqueness and non-reuse of identifiers are enforced by the rule
  registry added alongside the validation engine (also in this release). The
  reporters that render findings to files are not yet implemented.
- Automated secret scanning with [gitleaks](https://github.com/gitleaks/gitleaks),
  as a `Secret scanning` job in the existing CI workflow, running on pull
  requests and pushes to `main` over both the working tree and the full commit
  history. A detected credential fails the build. Configuration and a narrow,
  documented allowlist for synthetic placeholders live in `.gitleaks.toml`;
  local usage, remediation, and allowlisting guidance are documented in
  `CONTRIBUTING.md` and `docs/security-and-privacy.md`.

### Changed

- **Exit codes for `validate` (breaking).** The previously proposed three-code
  convention is now settled and implemented: `0` = parsed with no ERROR
  findings (WARNING and INFO alone still exit `0`), `1` = parsed but at least
  one ERROR finding, `2` = the manifest never reached the rule engine (missing
  or unreadable file, malformed YAML, non-mapping top level, or a
  structural/schema validation error). Previously every failure exited `1`;
  schema failures now exit `2`.

### Planned

Designed but not yet implemented (see the [README](README.md) and
[architecture](docs/architecture.md)):

- JSON and Markdown validation reports.
- RO-Crate 1.2 package creation via `ro-crate-py`.
- Optional enrichment of an existing nf-prov RO-Crate.
- Modality profiles (for example sequencing, imaging, mass spectrometry).

## [0.1.0] - 2026-07-19

Initial alpha. Establishes the repository, documentation set, data model, and a
minimal working CLI, using entirely synthetic, public-safe examples
(Milestone 0).

### Added

- `validate` command: reads a YAML run manifest, checks that the top level is a
  mapping, validates it against the typed `RunManifest` model, and prints a
  concise success summary. Pydantic validation errors are rendered as a table.
- `version` command: prints the installed package version.
- Typed `RunManifest` model (Pydantic v2) covering `manifest_version`, `run_id`,
  project, dataset, biological context (organism and optional tissue), assay,
  workflow, and input/output resources, with synthetic-identifier and
  format-pattern checks and rejection of unknown keys.
- Exit codes: `0` on success, `1` for any failure (missing or unreadable file,
  malformed YAML, non-mapping top level, or a validation error).
- Two synthetic example manifests (`examples/synthetic/valid-run.yaml` and
  `examples/synthetic/invalid-run.yaml`) and a test suite covering the CLI,
  parsing, and model behaviour.
- Documentation set: project charter, architecture, data model, roadmap,
  security and privacy policy, and architecture decision records.
- Apache-2.0 `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CITATION.cff`, and
  this changelog.
