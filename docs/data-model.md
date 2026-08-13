# Data Model — Bio Run Crate

**Status:** Implemented for Milestone 0. The Part A model below is realised as
Pydantic v2 models in `src/bio_run_crate/models.py`, loaded from YAML by
`src/bio_run_crate/manifest.py` and validated by the `validate` CLI command. All
examples on this page are public-safe: run, project, dataset and resource
identifiers, paths, instrument model names, and URLs are synthetic and invented,
using `example.org`-style values. Biological context may use real public
reference terminology and ontology/taxonomy identifiers. No example refers to a
real sample, patient, private organization, internal system, or production
dataset.

Validating a manifest happens in two distinct layers, and the distinction
matters throughout this document:

1. **Structural/schema validation (Pydantic).** Required fields, value types,
   non-empty required strings, synthetic-identifier patterns, and rejection of
   unknown keys (`extra="forbid"` on every model). A manifest that fails here is
   not a `RunManifest` at all, so no rule ever runs against it.
2. **Core validation rules (this project's rule engine).** Cross-field and
   semantic checks applied to an already-parsed manifest, each with a stable
   `CORE-NNN` identifier, emitting the structured findings described in §A.8.
   The core rule set is listed in §A.8.2 and implemented in
   `src/bio_run_crate/validation/`.

Both layers are implemented and wired into the `validate` CLI command. The JSON
and Markdown reporters that render findings to files are not yet built.

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
| `id` | string, pattern `input-<NNN>` / `output-<NNN>` | yes | Synthetic resource identifier. **Must be unique within its collection** — see below. |
| `path` | string (non-empty) | yes | Relative path or synthetic URI (`example.org` placeholder), never a real internal path. |
| `role` | string (non-empty) | yes | e.g. `"primary_input"`, `"result_table"`, `"qc_report"`. Free text at this level; profiles may constrain the allowed set. |
| `media_type` | string | no | MIME type or file-format label. |
| `checksum` | string | no | Recommended for outputs; a free-text digest label such as `"sha256:…"`. |

**Identifier uniqueness.** A resource `id` identifies exactly one entry within
its collection: no two `inputs` entries may share an `id`, and no two `outputs`
entries may share an `id`. This is what makes an identifier usable at all — a
finding, a report row, or an RO-Crate entity that refers to `input-001` must
resolve to one resource, not several. Inputs and outputs cannot collide with
each other, because their identifier patterns differ.

This is a **cross-field invariant**, not a per-field one: Pydantic's pattern
check validates each `id` in isolation and cannot see the rest of the list, so
uniqueness is enforced by rule `CORE-001` (§A.8.2) rather than by the schema.

Paths are deliberately *not* required to be unique. One file may legitimately be
described by two entries with different roles.

### A.8 Findings (produced by validation, not part of the manifest itself)

Findings are the *output* of validating a `RunManifest`, not an input
field. The structured findings model is **implemented** in
`src/bio_run_crate/findings.py`, and so is the rule engine that produces
findings (`src/bio_run_crate/validation/`, §A.8.2). The `validate` command runs
that engine and prints the findings it produces. What is *not* yet implemented
are the JSON and Markdown reporters that write them to files.

A `Finding` has:

| Field | Type | Notes |
|---|---|---|
| `rule_id` | string | Stable identifier, e.g. `CORE-001`. See §A.8.1, ADR-0003 and `docs/architecture.md` §3.4. |
| `severity` | enum | `ERROR`, `WARNING`, or `INFO` — exactly these three. |
| `message` | string | Human-readable, non-empty. |
| `location` | object | `{"path": "inputs[0].checksum"}`; defaults to the whole manifest, `"$"`. |

A `ValidationResult` aggregates the findings of one validation run in its
`findings` field. Both models are frozen (findings are never mutated in place)
and reject unknown fields, and both serialise to plain JSON types via Pydantic
(`model_dump(mode="json")` / `model_dump_json()`), with `severity` rendered as
its plain name.

A `ValidationResult` keeps its findings in **canonical order**: severity
(`ERROR`, then `WARNING`, then `INFO`), then location path, then rule ID, then
message. The order is applied by the model itself on every construction path —
the plain constructor, `model_validate`, JSON deserialisation, and the
`ValidationResult.from_findings(...)` convenience — so it is a property of the
result, not of how a caller chose to build it. Because the sort key is total
over everything that distinguishes one finding from another, the order the rule
engine happens to emit findings in cannot leak into report output, and equal
result contents always serialise to identical JSON. Sorting never mutates the
caller's own collection.

#### A.8.1 Rule-ID convention

A rule identifier is `<NAMESPACE>-<NNN>`:

- `NAMESPACE` — uppercase letters and digits, starting with a letter, 2–16
  characters. Core rules use `CORE`; each validation profile uses its own
  distinct namespace (ADR-0003).
- `NNN` — a zero-padded number of three or more digits.

Examples: `CORE-001`, `SEQ-014`. Rule IDs are part of the tool's public
surface — they may appear in audit records and suppression lists — so a rule's
severity or wording may change over time, but its identifier must not.

Two further invariants apply to the rule set as a whole: a number is **unique
within its namespace**, and an identifier is **never reused** once assigned.

The `Finding` model validates the *syntax* above (also exposed as
`bio_run_crate.findings.is_valid_rule_id`). It cannot check uniqueness or
reuse — a single finding has no view of the other rules.

Uniqueness **is** enforced at runtime: `RuleRegistry` refuses to build a rule set
containing two rules with the same identifier, so the core registry cannot be
constructed (and the package cannot be imported) if a duplicate is introduced.
A registry may also pin a namespace; the core registry pins `CORE`, so a rule
from a profile namespace cannot be added to the core rule set by mistake.

Non-reuse is a *historical* property that running code cannot infer — it can see
only the rules that exist now, not the ones that once did. It is therefore made
checkable by recording retirements explicitly: `RETIRED_CORE_RULE_IDS` in
`bio_run_crate.validation.core_rules` is a tombstone set, and the registry
rejects any rule whose identifier appears in it. Retiring a *published* rule
means deleting the rule *and* adding its identifier to that set; a retirement
that is never recorded still has to be caught by review. An identifier that was
only ever drafted and dropped before release was never something a user could
reference, so it needs no tombstone — it is simply left unallocated (§A.8.2).

#### A.8.2 Core rule set

The modality-agnostic core rules, implemented in
`src/bio_run_crate/validation/core_rules.py`. The set is deliberately minimal:
a rule ships only if it follows from something Part A already states. Each rule
is deterministic, offline, and does not read the filesystem — a manifest's paths
are never resolved or opened.

| Rule | Severity | Condition | Location | Why it is a core rule |
|---|---|---|---|---|
| `CORE-001` | ERROR | A resource `id` appears more than once within `inputs`, or within `outputs`. One finding per repeat occurrence. | `<collection>[<n>].id` of each repeat | §A.7 requires a resource `id` to be unique within its collection. Without that, an identifier does not identify: any finding, report row or RO-Crate entity naming `input-001` would be ambiguous, so the generic model cannot be coherent while permitting duplicates. It is a cross-field invariant — Pydantic's per-field pattern check cannot see the rest of the list — which is exactly why it is a rule rather than schema. |
| `CORE-003` | WARNING | An output has no `checksum`. | `outputs[<n>].checksum` | §A.7 states a checksum is *recommended for outputs*. A documented recommendation that is not met is "acceptable but questionable", the definition of WARNING. It is not applied to inputs, which carry no such recommendation. |

`CORE-002`, `CORE-004` and `CORE-005` are unallocated: they were drafted during
development (duplicate resource paths, empty `outputs`, empty `inputs`) and
dropped before release, because each would have created product policy the model
does not state — §A.1 explicitly permits empty collections, and §A.7 explicitly
does not require unique paths. They are open design questions (§A.9), not rules.
Because they were never present in a released version, no user could have
referenced them, so they are *not* tombstoned in `RETIRED_CORE_RULE_IDS` — that
set is reserved for identifiers that were genuinely published. They are simply
left unused.

Also deliberately excluded: any restatement of a Pydantic check (that would
duplicate structural validation rather than add to it); any check of `checksum`
*format*, `role` vocabulary, or `media_type` values (each needs a product
decision Part A has not made — see §A.9); any check comparing `dataset.created`
against the current date (non-deterministic); and anything requiring the
filesystem, an ontology, the network, or knowledge of a specific modality.

Each rule declares exactly one severity, and the engine enforces that a rule
never emits a finding at any other severity. Severity is therefore a property of
the rule ID: a reader of an audit record or suppression list can reason about
`CORE-001` without knowing which manifest produced it. A condition that needs
reporting at two severities is two rules with two identifiers.

### A.9 Open questions (generic model)

- Whether `Resource.role` should become a constrained enum at the core
  level, or remain free text with constraints only added by profiles.
- Whether `checksum` should become a structured object (`algorithm` + `value`)
  rather than the current free-text label, once outputs are checksummed in
  practice, and whether its *format* should then be validated.
- Whether two resource entries sharing a `path` should be reported. It is
  currently permitted (one file, two roles) and not flagged; treating it as a
  probable copy-paste mistake would be a new policy, and needs agreement on
  whether the legitimate case is common enough to matter.
- Whether an empty `outputs` list (a run that describes nothing it produced) or
  an empty `inputs` list should be reported, and at what severity. §A.1
  explicitly permits both today, so flagging either would change the agreed
  contract rather than validate it.
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
listing below is a copy for reference. Deliberately defective counterparts live
alongside it, each annotated inline with the defect it carries:

| Example | Failure mode | Where it fails |
|---|---|---|
| `missing-required-field-run.yaml` | Required field missing: `workflow.version` is omitted (§A.6). | Schema (`missing` at `workflow.version`) |
| `wrong-field-type-run.yaml` | Wrong field type: `inputs` is a scalar rather than a list of resources (§A.7). | Schema (`list_type` at `inputs`) |
| `duplicate-output-id-run.yaml` | Identifier reused: `output-001` names two outputs, breaking the uniqueness contract in §A.7. | Rule `CORE-001` (ERROR) at `outputs[1].id` |
| `invalid-run.yaml` | Several structural defects at once: malformed `run_id` and `project.id`, missing `organism.scientific_name` and `workflow.version`, unknown top-level key. | Schema |
| `rule-violations-run.yaml` | Several core-rule violations at once. | Rules `CORE-001` (ERROR) and `CORE-003` (WARNING) (§A.8.2) |

The first three isolate a single defect each, so one diagnostic can be studied on
its own; the last two bundle defects to show several being reported together. A
manifest that fails schema validation never reaches the rule engine, so no rule
runs against it.

Note that the valid manifest below still produces one `CORE-003` WARNING:
`output-002` carries no checksum. That is intentional — it keeps a
warning-producing case in the canonical example — and it does not stop the
manifest being valid or the command exiting `0`.

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

This example is used purely to illustrate the schema described in Part A. Its
run-specific identifiers, paths, project and dataset metadata, and URLs are
synthetic; its workflow and instrument names are placeholders; and it names no
real reference genome. The organism and tissue terms are public reference
vocabulary (`Homo sapiens`, `NCBI:txid9606`, `UBERON:0002107`) and identify no
real sample, patient, private organization, internal system or production
dataset.
