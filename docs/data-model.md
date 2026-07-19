# Data Model — Bio Run Crate

**Status:** Target design for Milestone 0. No Pydantic models exist in the
repository yet; this document specifies the model that implementation
should follow. All examples on this page are entirely synthetic — invented
identifiers, invented instrument model names, and `example.org`-style
values. None refer to any real organization, system, or dataset.

This document is split into two clearly separated parts, per project
scope:

- **Part A — the generic biological run model.** Modality-agnostic. Every
  manifest must satisfy this regardless of what kind of experiment
  produced it.
- **Part B — optional modality profiles.** Illustrative extensions that
  add modality-specific fields and rules on top of Part A. Profiles are
  optional, additive, and none are required for the core tool to function.

## Part A — Generic run model

The generic model describes four things: what produced the run, what went
into it, what came out of it, and how it was executed. It intentionally
avoids any field that only makes sense for one experimental technique.

### A.1 `RunManifest` (top-level object)

| Field | Type | Required | Notes |
|---|---|---|---|
| `manifest_version` | string | yes | Version of the manifest schema itself, independent of the tool version. |
| `run_id` | string | yes | Stable, unique, synthetic identifier for the run (e.g. `run-0007`). Must not be a real sample or specimen ID. |
| `name` | string | yes | Short human-readable run name. |
| `description` | string | no | Free-text description. |
| `created_at` | timestamp (ISO 8601) | yes | When the manifest was authored. |
| `profile` | list of strings | no | Zero or more modality profile identifiers to apply (see Part B). Empty/absent means core-only validation. |
| `analysis` | `Analysis` object | yes | See A.2. |
| `inputs` | list of `Artifact` | yes | May be empty for a run with no external inputs, but the field itself must be present. |
| `outputs` | list of `Artifact` | yes | |
| `provenance` | `Provenance` object | yes | See A.5. |

### A.2 `Analysis`

Describes what was run, independent of any specific workflow engine.

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | e.g. `"synthetic-variant-demo"`. |
| `version` | string | yes | Version of the analysis/pipeline itself. |
| `parameters` | mapping (string → scalar) | no | Flat key/value parameters. Nested/structured parameters are an open question (A.7). |
| `software` | list of `SoftwareComponent` | yes | At least the primary tool; may list more. |

### A.3 `SoftwareComponent`

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | |
| `version` | string | yes | |
| `container_or_env` | string | no | Free-text reference to a container image or environment spec, if used. Never a private registry path in examples. |

### A.4 `Artifact` (used for both inputs and outputs)

| Field | Type | Required | Notes |
|---|---|---|---|
| `path` | string | yes | Relative path or synthetic URI (e.g. `example.org` placeholder), never a real internal path. |
| `role` | string | yes | e.g. `"primary_input"`, `"result_table"`, `"qc_report"`. Free text at this level; profiles may constrain the allowed set. |
| `media_type` | string | no | MIME type or file-format label. |
| `checksum` | `Checksum` object | no | Recommended for outputs; see below. |
| `size_bytes` | integer | no | |

`Checksum`:

| Field | Type | Required |
|---|---|---|
| `algorithm` | string (e.g. `"sha256"`) | yes |
| `value` | string | yes |

### A.5 `Provenance`

Minimal, workflow-engine-agnostic provenance linking inputs to outputs
through the analysis.

| Field | Type | Required | Notes |
|---|---|---|---|
| `executed_at` | timestamp | yes | |
| `executor` | string | no | A role or system label (e.g. `"ci-pipeline"`, `"maintainer-workstation"`), never a real person's name or email — see `docs/security-and-privacy.md`. |
| `source_crate` | string | no | Present only if this manifest is associated with, or was derived from metadata in, an existing RO-Crate (for example one produced by nf-prov). This is a pointer, not a copy of that crate's contents. |

### A.6 Findings (produced by validation, not part of the manifest itself)

Findings are the *output* of validating a `RunManifest`, not an input
field. Each finding has:

| Field | Type | Notes |
|---|---|---|
| `rule_id` | string | Stable identifier, e.g. `CORE-001`. See ADR-0003 and `docs/architecture.md` §3.4. |
| `severity` | enum | `ERROR`, `WARNING`, or `INFO`. |
| `message` | string | Human-readable. |
| `path` | string | Location within the manifest the finding refers to (e.g. `inputs[0].checksum`). |

### A.7 Open questions (generic model)

- Whether `parameters` should support nested structures (mappings of
  mappings/lists) or stay intentionally flat for determinism and
  diffability.
- Whether `Artifact.role` should become a constrained enum at the core
  level, or remain free text with constraints only added by profiles.
- How multi-sample or multi-run batch manifests (as opposed to one manifest
  per run) would be represented, if ever needed — currently out of scope.

## Part B — Optional modality profiles

Profiles are **illustrative and not implemented** as of this document.
They exist here to show how modality-specific concerns would attach to the
generic model without polluting it. A profile may:

- add required or optional fields to specific parts of the manifest (most
  commonly to `Artifact` entries or `Analysis.parameters`), and
- contribute additional validation rules with their own rule-ID prefix.

None of the profile field names or value sets below should be treated as
final — they are placeholders to demonstrate the extension pattern.

### B.1 Example: sequencing profile (illustrative only)

Might add to each relevant `Artifact`:

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

```yaml
manifest_version: "0.1"
run_id: "run-0007"
name: "synthetic-demo-run"
description: "Fully synthetic example run for documentation purposes only."
created_at: "2026-01-15T09:00:00Z"
profile: []   # core-only; no modality profile applied in this example

analysis:
  name: "synthetic-variant-demo"
  version: "0.1.0"
  parameters:
    min_quality: 30
    reference: "synthetic-reference-genome-v1"
  software:
    - name: "synthetic-aligner"
      version: "1.2.3"
      container_or_env: "example.org/synthetic-aligner:1.2.3"

inputs:
  - path: "inputs/reads_R1.fastq.gz"
    role: "primary_input"
    media_type: "application/gzip"
    checksum:
      algorithm: "sha256"
      value: "0000000000000000000000000000000000000000000000000000000000aa"
    size_bytes: 104857600

outputs:
  - path: "outputs/variants.vcf.gz"
    role: "result_table"
    media_type: "application/gzip"
    checksum:
      algorithm: "sha256"
      value: "0000000000000000000000000000000000000000000000000000000000bb"
    size_bytes: 2048000
  - path: "outputs/qc_report.md"
    role: "qc_report"
    media_type: "text/markdown"

provenance:
  executed_at: "2026-01-15T09:42:00Z"
  executor: "ci-pipeline"
  source_crate: null
```

This example is used purely to illustrate the schema described in Part A.
It contains no real identifiers, no real reference genome, and no real
software beyond a synthetic placeholder name.
