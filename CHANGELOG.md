# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
While the project is pre-1.0 (`0.x`), minor versions may include breaking
changes.

## [Unreleased]

### Added

- Structured validation findings in `bio_run_crate.findings`: a `Severity`
  enumeration limited to `ERROR`, `WARNING` and `INFO`; a frozen `Finding`
  model carrying a stable rule identifier, severity, message and a `Location`
  into the manifest; and a `ValidationResult` container that holds its findings
  in a canonical, deterministic order on every construction path. Both models
  are JSON-serialisable. The rule-ID syntax (`<NAMESPACE>-<NNN>`, core rules
  under `CORE`) is documented in `docs/data-model.md` §A.8.1 and validated by the
  model; uniqueness and non-reuse of identifiers are project-level invariants for
  the future rule registry to enforce. The rule engine that produces findings
  and the reporters that render them are not yet implemented, so the CLI does
  not use this model yet.
- Automated secret scanning with [gitleaks](https://github.com/gitleaks/gitleaks),
  as a `Secret scanning` job in the existing CI workflow, running on pull
  requests and pushes to `main` over both the working tree and the full commit
  history. A detected credential fails the build. Configuration and a narrow,
  documented allowlist for synthetic placeholders live in `.gitleaks.toml`;
  local usage, remediation, and allowlisting guidance are documented in
  `CONTRIBUTING.md` and `docs/security-and-privacy.md`.

### Planned

Designed but not yet implemented (see the [README](README.md) and
[architecture](docs/architecture.md)):

- The validation-rule engine that produces findings.
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
