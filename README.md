# bio-run-crate

![Status: alpha](https://img.shields.io/badge/status-alpha-orange)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
![Python: 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![Linting: Ruff](https://img.shields.io/badge/lint-ruff-informational)
![Types: mypy](https://img.shields.io/badge/types-mypy%20strict-informational)

A general-purpose, offline command-line tool that validates biological
analysis-run metadata described in a YAML manifest. Its longer-term goal is to
produce structured validation reports and to create or enrich
[RO-Crate](https://www.researchobject.org/ro-crate/) packages, so that
computational-biology results of any modality (sequencing, imaging, mass
spectrometry, and others) can carry consistent, checkable metadata independent
of the workflow engine, LIMS, or notebook that produced them.

Bio Run Crate is a metadata-validation and packaging utility. It is **not** a
LIMS, a workflow engine, or a data catalog.

> ⚠️ **Alpha / work in progress.** This project is at **Milestone 0**. Today it
> can parse and validate a YAML manifest against a typed model and report the
> result with clear exit codes. Structured findings, JSON/Markdown reports, and
> RO-Crate output are **designed but not yet built** — see
> [Current capabilities](#current-capabilities) and
> [Planned capabilities](#planned-capabilities). Interfaces may change without
> notice while the project is pre-1.0.

## Table of contents

- [Why bio-run-crate exists](#why-bio-run-crate-exists)
- [Current capabilities](#current-capabilities)
- [Planned capabilities](#planned-capabilities)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Manifest example](#manifest-example)
- [CLI reference](#cli-reference)
- [Exit codes](#exit-codes)
- [What is RO-Crate?](#what-is-ro-crate)
- [Relationship to nf-prov](#relationship-to-nf-prov)
- [Architecture overview](#architecture-overview)
- [Manifest data model](#manifest-data-model)
- [Privacy and security](#privacy-and-security)
- [Roadmap](#roadmap)
- [Limitations](#limitations)
- [Development](#development)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)
- [Disclaimer](#disclaimer)
- [Documentation](#documentation)

## Why bio-run-crate exists

Analysis-run metadata is frequently inconsistent, incomplete, or captured in ad
hoc formats that differ from team to team and modality to modality. That makes it
hard to confirm a run's metadata is complete enough to trust before results are
used downstream, to package a run's inputs, parameters, and outputs in a
portable standards-based format, and to apply consistent, auditable checks across
many runs.

Bio Run Crate addresses the **metadata-validation and packaging** layer of this
problem. You describe a run in a small YAML manifest; the tool checks that
manifest against explicit, typed rules and (in future milestones) emits
structured reports and a standards-based RO-Crate package. It deliberately does
**not** handle instrument integration, sample tracking, or long-term storage.

See the [project charter](docs/project-charter.md) for the full scope and
non-goals.

## Current capabilities

These work today and are covered by tests:

- **`validate` command** — reads a YAML manifest, checks that the top level is a
  mapping, validates it against the typed `RunManifest` model, and prints a
  concise one-line success summary on success.
- **`version` command** — prints the installed package version.
- **Typed manifest model** — a [Pydantic v2](https://docs.pydantic.dev/) model
  covering the project, dataset, biological context (organism and optional
  tissue), assay, workflow, and input/output resources. It enforces required
  fields, value types, non-empty strings, synthetic-identifier patterns, and
  **rejects unknown keys**.
- **Clear error reporting** — validation errors are rendered as a table of the
  offending locations (so multiple problems are visible at once), printed to
  **stderr**; the success summary goes to **stdout**.
- **Deterministic exit codes** — `0` on success, `1` for any failure. See
  [Exit codes](#exit-codes).
- **Synthetic examples** — one valid and one intentionally invalid manifest, used
  by the test suite.

## Planned capabilities

These are designed in the docs but **not yet implemented**; the CLI does not
perform them today:

- **Structured findings** with stable rule IDs and ERROR / WARNING / INFO
  severities. (Today the CLI surfaces Pydantic's built-in validation errors
  directly, not project-defined rule findings.)
- **JSON and Markdown validation reports.**
- **RO-Crate 1.2 package creation** via
  [`ro-crate-py`](https://www.researchobject.org/ro-crate/). (`rocrate` is
  declared as a dependency in preparation, but no RO-Crate code exists yet.)
- **Optional enrichment of an existing
  [nf-prov](https://github.com/nextflow-io/nf-prov) RO-Crate.**
- **Modality profiles** (for example sequencing, imaging, mass spectrometry),
  which are illustrative only in [`docs/data-model.md`](docs/data-model.md).

Progress against these is tracked in the [roadmap](docs/roadmap.md).

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/) for environment and dependency management

## Installation

Clone the repository and synchronise the environment:

```
uv sync
```

This installs the project and its dependencies into a managed virtual
environment. There is no published package on a package index yet.

## Quick start

```
# Print the installed version
uv run bio-run-crate version

# Validate a manifest that passes (exits 0)
uv run bio-run-crate validate examples/synthetic/valid-run.yaml

# Validate a manifest that fails (exits 1, prints an error table)
uv run bio-run-crate validate examples/synthetic/invalid-run.yaml
```

A valid manifest prints a short success summary and exits `0`. Any failure — a
missing or unreadable file, malformed YAML, a non-mapping top level, or a
validation error — prints an error and exits `1`, with validation errors shown as
a table so multiple problems are visible at once.

## Manifest example

The manifest below is fully synthetic and matches the current model. Every
identifier, name, and URL is invented; nothing refers to a real organism sample,
organization, system, or dataset. It is a copy of
[`examples/synthetic/valid-run.yaml`](examples/synthetic/valid-run.yaml).

```yaml
manifest_version: "0.1"
run_id: run-001

project:
  id: project-001
  title: Synthetic transcriptomics demonstration
  description: A fully synthetic example project for testing bio-run-crate.
  url: https://example.org/projects/project-001

dataset:
  id: dataset-001
  title: Synthetic RNA-seq dataset
  description: Invented dataset used purely for documentation and tests.
  created: 2026-01-15

biological_context:
  organism:
    scientific_name: Homo sapiens
    taxon_id: NCBI:txid9606
    common_name: human
  tissue:
    name: liver
    ontology_id: UBERON:0002107

assay:
  type: synthetic-rna-seq
  platform: synthetic-sequencing
  instrument_model: synthetic-sequencer-x

workflow:
  name: synthetic-rnaseq-workflow
  version: "1.0.0"
  url: https://example.org/workflows/synthetic-rnaseq-workflow

inputs:
  - id: input-001
    path: inputs/reads_R1.fastq.gz
    role: primary_input
    media_type: application/gzip
    checksum: sha256:00000000000000000000000000000000000000000000000000000000000000aa

outputs:
  - id: output-001
    path: outputs/counts.tsv
    role: result_table
    media_type: text/tab-separated-values
  - id: output-002
    path: outputs/qc_report.md
    role: qc_report
    media_type: text/markdown
```

An intentionally invalid counterpart is provided at
[`examples/synthetic/invalid-run.yaml`](examples/synthetic/invalid-run.yaml),
with each defect annotated inline.

## CLI reference

Running `bio-run-crate` with no arguments prints help. Two commands exist:

| Command | Arguments | Description |
|---|---|---|
| `version` | — | Print the installed package version and exit. |
| `validate` | `MANIFEST` (path to a YAML file) | Parse and validate a run manifest against the `RunManifest` model. Prints a success summary on stdout, or an error and a table of validation problems on stderr. |

```
uv run bio-run-crate --help
uv run bio-run-crate validate --help
```

## Exit codes

The `validate` command uses two exit codes today:

| Code | Meaning |
|---|---|
| `0` | The manifest is valid. |
| `1` | Any failure: file not found or unreadable, malformed YAML, a non-mapping top level, or a model validation error. |

> A finer-grained scheme that distinguishes "validation failed" (`1`) from "the
> tool itself could not run" (`2`) is proposed in
> [`docs/architecture.md`](docs/architecture.md) but is **not yet implemented** —
> today all failures return `1`.

## What is RO-Crate?

[RO-Crate](https://www.researchobject.org/ro-crate/) (Research Object Crate) is a
community standard for packaging research data together with structured,
machine-readable metadata, using [schema.org](https://schema.org/) terms
expressed as JSON-LD. In practice, an RO-Crate is a directory (or archive)
containing your data files plus an `ro-crate-metadata.json` file that describes
them and how they relate.

Bio Run Crate's longer-term goal is to describe a validated analysis run — its
project, dataset, biological context, workflow, inputs, and outputs — as an
RO-Crate 1.2 package, so results can travel with consistent, checkable metadata.
The RO-Crate reading/writing itself is delegated to the
[`ro-crate-py`](https://www.researchobject.org/ro-crate/) library rather than
reimplemented here. **This output is planned, not yet implemented** (see
[Planned capabilities](#planned-capabilities) and
[ADR-0002](docs/decisions/ADR-0002-use-ro-crate-1.2.md)).

## Relationship to nf-prov

[nf-prov](https://github.com/nextflow-io/nf-prov) is a Nextflow plugin that
captures provenance for pipelines run with Nextflow, optionally emitting an
RO-Crate. Bio Run Crate is designed to **complement** nf-prov, not replace it:

- It does **not** reimplement or replace nf-prov's provenance capture.
- In a future milestone it will be able to treat an nf-prov-produced RO-Crate as
  one possible **input** that an enrichment step extends with additional
  validated metadata.

This enrichment path is **planned, not yet implemented**, and is one of the
least-defined parts of the design — see
[`docs/architecture.md`](docs/architecture.md) §6 and the roadmap.

## Architecture overview

Bio Run Crate keeps parsing, validation, reporting, and RO-Crate generation as
separate components with narrow interfaces. At a high level:

```
CLI (Typer)
  → Manifest parsing (PyYAML → dict → Pydantic models)   [implemented]
  → Validation                                            [today: model-level; rule engine planned]
  → Findings (ERROR / WARNING / INFO)                     [planned]
  → Reports (JSON + Markdown)                             [planned]
  → RO-Crate generation / enrichment (ro-crate-py)        [planned]
```

Today the CLI wires together manifest parsing and model validation. The
standalone validation-rule engine, findings model, report generators, and
RO-Crate layer are still target design. Two adjacent responsibilities are
deliberately delegated to existing tools rather than reimplemented: workflow
execution and Nextflow provenance capture (nf-prov), and RO-Crate serialization
(ro-crate-py). See [`docs/architecture.md`](docs/architecture.md) for the full
picture and the architecture decision records in
[`docs/decisions/`](docs/decisions/).

## Manifest data model

A manifest is a single YAML mapping validated against the `RunManifest` model
(`src/bio_run_crate/models.py`). Its top-level fields are:

| Field | Type | Notes |
|---|---|---|
| `manifest_version` | string | Required, non-empty. |
| `run_id` | string | Required; must match `run-<NNN>` (e.g. `run-001`). |
| `project` | object | `id` matches `project-<NNN>`; required `title`; optional `description`, `url`. |
| `dataset` | object | `id` matches `dataset-<NNN>`; required `title`; optional `description`, `created` (date). |
| `biological_context` | object | Required `organism` (`scientific_name`, optional `taxon_id` as `NCBI:txid…`, optional `common_name`); optional `tissue` (`name`, optional `ontology_id` as `UBERON:…`). |
| `assay` | object | Required `type`; optional `platform`, `instrument_model`. |
| `workflow` | object | Required `name` and `version`; optional `url`. |
| `inputs` | list | Each item has `id` matching `input-<NNN>`, plus `path`, `role`, optional `media_type`, `checksum`. |
| `outputs` | list | Each item has `id` matching `output-<NNN>`, plus `path`, `role`, optional `media_type`, `checksum`. |

Every object rejects unknown keys. The identifier patterns (such as `run-001`,
`project-001`) deliberately keep examples anchored to invented, public-safe
values — real sample or specimen identifiers must never appear in a manifest
committed to this repository. The illustrative **modality profiles** described in
[`docs/data-model.md`](docs/data-model.md) are not yet implemented.

## Privacy and security

- **Offline core.** Reading and validating a manifest requires no network access
  and no credentials.
- **Synthetic data only, in this repository.** All examples, fixtures, and
  documentation use invented identifiers and `example.org`-style placeholders —
  never real sample IDs, organization names, internal systems, or personal data.
- **Safe parsing.** YAML is parsed with safe loading, not arbitrary object
  deserialization.
- **No silent mutation.** The tool does not rewrite or "fix" your source
  manifest.

See [`docs/security-and-privacy.md`](docs/security-and-privacy.md) for the full
policy and [`SECURITY.md`](SECURITY.md) for how to report a vulnerability.

## Roadmap

- **Current (Milestone 0):** repository, documentation, typed data model, and a
  minimal `validate` CLI over synthetic examples. Manifest parsing, the typed
  model, and the CLI are done; the rule engine, findings, reports, and RO-Crate
  output are not.
- **Next (candidate, not committed):** the core validation-rule engine with
  stable rule IDs and ERROR/WARNING/INFO findings; JSON and Markdown reports;
  RO-Crate 1.2 output; the first real modality profile; nf-prov enrichment.
- **Later (speculative):** additional profiles, a plugin mechanism for
  third-party profiles, batch/multi-run manifests, and any strictly optional
  network-dependent feature.

Nothing on the roadmap is a dated commitment. See
[`docs/roadmap.md`](docs/roadmap.md) for the authoritative, ordered list.

## Limitations

- Alpha software; interfaces and the manifest schema may change without notice
  while the project is pre-1.0.
- Validation today is **model-level only** (required fields, types, non-empty
  strings, identifier/format patterns, unknown-key rejection). There is no
  cross-field rule engine, no rule IDs, and no WARNING/INFO severities yet.
- No report files are produced; results are printed to the terminal only.
- No RO-Crate is created, and no nf-prov crate can be imported yet.
- No modality-specific profiles are implemented.
- The tool is not published to a package index; install from source with `uv`.

## Development

Run every check before declaring work complete:

```
uv run pytest                    # tests
uv run ruff check .              # lint
uv run ruff format --check .     # formatting
uv run mypy src                  # type checking
```

Build the distribution artifacts:

```
uv build
```

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for
the development setup, the required checks, and the project's ground rules —
especially the **synthetic-data-only** and **no-secrets** rules in
[`docs/security-and-privacy.md`](docs/security-and-privacy.md). Security issues
should be reported privately following [`SECURITY.md`](SECURITY.md), not as a
public issue.

## Citation

If you use bio-run-crate in your work, please cite it. Machine-readable metadata
is provided in [`CITATION.cff`](CITATION.cff), and notable changes are recorded
in [`CHANGELOG.md`](CHANGELOG.md).

## License

Licensed under the [Apache License 2.0](LICENSE). Unless you explicitly state
otherwise, any contribution you submit is provided under the same license
(inbound = outbound), per Section 5 of the Apache-2.0 text.

## Disclaimer

Bio Run Crate is an independent, community open-source project. It is not
affiliated with, endorsed by, or sponsored by any organization, employer, or the
maintainers of the RO-Crate, ro-crate-py, nf-prov, or Nextflow projects. Those
names are used only to describe interoperability. The project makes no claims of
compliance with any regulatory framework; adopters are responsible for how they
classify and handle their own data when they run the tool.

## Documentation

- [Project charter](docs/project-charter.md) — purpose, scope, and non-goals.
- [Architecture](docs/architecture.md) — component boundaries and what is built
  versus planned.
- [Data model](docs/data-model.md) — the manifest schema and modality profiles.
- [Roadmap](docs/roadmap.md) — milestone tracking.
- [Security and privacy](docs/security-and-privacy.md) — the synthetic-data and
  no-secrets policy.
- [Architecture decision records](docs/decisions/) — ADRs.
