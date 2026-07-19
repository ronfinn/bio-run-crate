# Data Model — Bio Run Crate

**Status:** Implemented for Milestone 0. The Part A model below is realised as
Pydantic v2 models in `src/bio_run_crate/models.py`, loaded from YAML by
`src/bio_run_crate/manifest.py` and validated by the `validate` CLI command. All
examples on this page are entirely synthetic — invented identifiers, invented
instrument model names, and `example.org`-style values. None refer to any real
organization, system, or dataset.

Validation at this milestone uses Pydantic's built-in errors only: required
fields, value types, non-empty required strings, synthetic-identifier patterns,
and rejection of unknown keys (`extra="forbid"` on every model). The structured
findings system in §A.6 (stable rule IDs and ERROR/WARNING/INFO severities) is a
later milestone and is not yet implemented.

This document is split into two clearly separated parts, per project
scope:

- **Part A — the generic biological run model.** Modality-agnostic. Every
  manifest must satisfy this regardless of what kind of experiment
  produced it.
- **Part B — optional modality profiles.** Illustrative extensions that
  add modality-specific fields and rules on top of Part A. Profiles are
  optional, additive, and none are required for the core tool to function.

## Part A — Generic run model

The generic model describes what a run belongs to (project and dataset), what
its material is (biological context), how the data was measured and analysed
(assay and workflow), and what went in and came out (input and output
resources). It intentionally avoids any field that only makes sense for one
experimental technique; modality-specific fields belong to profiles (Part B).

Synthetic-identifier patterns are enforced so examples stay anchored to invented,
public-safe values and never carry a real sample or specimen ID. Where a pattern
is given below (e.g. `project-<NNN>`), `<NNN>` is three or more digits.

### A.1 `RunManifest` (top-level object)

| Field | Type | Required | Notes |
|---|---|---|---|
| `manifest_version` | string (non-empty) | yes | Version of the manifest schema itself, independent of the tool version. |
| `run_id` | string, pattern `run-<NNN>` | yes | Stable, synthetic identifier for the run (e.g. `run-001`). Must not be a real sample or specimen ID. |
| `project` | `Project` object | yes | See A.2. |
| `dataset` | `Dataset` object | yes | See A.3. |
| `biological_context` | `BiologicalContext` object | yes | See A.4. |
| `assay` | `Assay` object | yes | See A.5. |
| `workflow` | `Workflow` object | yes | See A.6. |
| `inputs` | list of `InputResource` | yes | May be empty, but the field itself must be present. See A.7. |
| `outputs` | list of `OutputResource` | yes | May be empty, but the field itself must be present. See A.7. |

### A.2 `Project`

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string, pattern `project-<NNN>` | yes | Synthetic project identifier, e.g. `project-001`. |
| `title` | string (non-empty) | yes | Short human-readable project title. |
| `description` | string | no | Free-text description. |
| `url` | URL | no | `example.org`-style placeholder only; never an internal or private URL. |

### A.3 `Dataset`

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string, pattern `dataset-<NNN>` | yes | Synthetic dataset identifier, e.g. `dataset-001`. |
| `title` | string (non-empty) | yes | Short human-readable dataset title. |
| `description` | string | no | Free-text description. |
| `created` | date (ISO 8601) | no | Date the dataset was created. |

### A.4 `BiologicalContext`

Describes what the run's material is, biologically.

| Field | Type | Required | Notes |
|---|---|---|---|
| `organism` | `Organism` object | yes | See below. |
| `tissue` | `Tissue` object | no | Optional: not every run has a tissue source (e.g. a cell line or microbial culture). |

`Organism`:

| Field | Type | Required | Notes |
|---|---|---|---|
| `scientific_name` | string (non-empty) | yes | e.g. `"Homo sapiens"`. |
| `taxon_id` | string, pattern `NCBI:txid<N>` | no | e.g. `NCBI:txid9606`. |
| `common_name` | string | no | e.g. `"human"`. |

`Tissue`:

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string (non-empty) | yes | e.g. `"liver"`. |
| `ontology_id` | string, pattern `UBERON:<7 digits>` | no | e.g. `UBERON:0002107`. |

### A.5 `Assay`

The measurement or assay that generated the data.

| Field | Type | Required | Notes |
|---|---|---|---|
| `type` | string (non-empty) | yes | e.g. `"synthetic-rna-seq"`. |
| `platform` | string | no | e.g. `"synthetic-sequencing"`. |
| `instrument_model` | string | no | Synthetic placeholder value only, e.g. `"synthetic-sequencer-x"`. |

### A.6 `Workflow`

The analysis workflow that produced the run, independent of any specific
workflow engine.

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string (non-empty) | yes | e.g. `"synthetic-rnaseq-workflow"`. |
| `version` | string (non-empty) | yes | Version of the workflow itself. |
| `url` | URL | no | `example.org`-style placeholder only. |

### A.7 `InputResource` / `OutputResource`

Both share a common `Resource` shape and differ only in the pattern their `id`
must match (`input-<NNN>` for inputs, `output-<NNN>` for outputs).

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string, pattern `input-<NNN>` / `output-<NNN>` | yes | Synthetic resource identifier. |
| `path` | string (non-empty) | yes | Relative path or synthetic URI (`example.org` placeholder), never a real internal path. |
| `role` | string (non-empty) | yes | e.g. `"primary_input"`, `"result_table"`, `"qc_report"`. Free text at this level; profiles may constrain the allowed set. |
| `media_type` | string | no | MIME type or file-format label. |
| `checksum` | string | no | Recommended for outputs; a free-text digest label such as `"sha256:…"`. |

### A.8 Findings (produced by validation, not part of the manifest itself)

Findings are the *output* of validating a `RunManifest`, not an input
field. This structured findings model is **not yet implemented** — at this
milestone the CLI surfaces Pydantic's built-in errors directly. When built,
each finding will have:

| Field | Type | Notes |
|---|---|---|
| `rule_id` | string | Stable identifier, e.g. `CORE-001`. See ADR-0003 and `docs/architecture.md` §3.4. |
| `severity` | enum | `ERROR`, `WARNING`, or `INFO`. |
| `message` | string | Human-readable. |
| `path` | string | Location within the manifest the finding refers to (e.g. `inputs[0].checksum`). |

### A.9 Open questions (generic model)

- Whether `Resource.role` should become a constrained enum at the core
  level, or remain free text with constraints only added by profiles.
- Whether `checksum` should become a structured object (`algorithm` + `value`)
  rather than the current free-text label, once outputs are checksummed in
  practice.
- How multi-sample or multi-run batch manifests (as opposed to one manifest
  per run) would be represented, if ever needed — currently out of scope.

## Part B — Optional modality profiles

Profiles are **illustrative and not implemented** as of this document.
They exist here to show how modality-specific concerns would attach to the
generic model without polluting it. A profile may:

- add required or optional fields to specific parts of the manifest (most
  commonly to resource entries or the `assay`/`workflow` objects), and
- contribute additional validation rules with their own rule-ID prefix.

None of the profile field names or value sets below should be treated as
final — they are placeholders to demonstrate the extension pattern.

### B.1 Example: sequencing profile (illustrative only)

Might add to each relevant resource entry:

| Field | Type | Notes |
|---|---|---|
| `read_type` | string | e.g. `"single-end"`, `"paired-end"` (illustrative) |
| `instrument_model` | string | Synthetic placeholder value only, e.g. `"synthetic-sequencer-x"` |
| `library_strategy` | string | e.g. `"synthetic-wgs"` |

### B.2 Example: imaging profile (illustrative only)

| Field | Type | Notes |
|---|---|---|
| `modality` | string | e.g. `"synthetic-fluorescence"` |
| `channel_count` | integer | |
| `magnification` | string | |

### B.3 Example: mass spectrometry profile (illustrative only)

| Field | Type | Notes |
|---|---|---|
| `acquisition_mode` | string | e.g. `"synthetic-dda"` |
| `instrument_model` | string | Synthetic placeholder value only |

### B.4 Open questions (profiles)

- Whether profiles are distributed as part of this repository, as
  separate installable packages, or both (see ADR-0003).
- Whether a manifest may declare more than one profile at once, and how
  conflicting field requirements between profiles would be resolved.
- The actual field sets above are placeholders and must be validated
  against real community conventions (e.g. existing minimal-information
  checklists for each modality) before being finalized — this should not
  be done from memory; it needs deliberate research and citation.

## Part C — Fully synthetic example manifest

The canonical copy of this manifest lives at
`examples/synthetic/valid-run.yaml` and is exercised by the test suite; the
listing below is a copy for reference. A deliberately invalid counterpart lives
at `examples/synthetic/invalid-run.yaml`.

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
    checksum: sha256:00000000000000000000000000000000000000000000000000000000000000bb
  - id: output-002
    path: outputs/qc_report.md
    role: qc_report
    media_type: text/markdown
```

This example is used purely to illustrate the schema described in Part A.
It contains no real identifiers, no real reference genome, and no real
software beyond synthetic placeholder names.
