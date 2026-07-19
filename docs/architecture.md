# Architecture — Bio Run Crate

**Status:** Partly implemented for Milestone 0. The manifest-parsing and
generic-run-model components below now exist (`src/bio_run_crate/manifest.py`,
`models.py`) and are wired into the `validate` CLI command; the validation-rule
engine, report generation and RO-Crate output are still target design. This
document should be updated to reflect reality as components are built, per the
workflow rule in `CLAUDE.md` ("update documentation when behaviour changes").

## 1. Scope boundary

This project is responsible for four things: reading a manifest, validating
it, reporting findings, and producing/enriching an RO-Crate package. It
relies on external, already-existing tools for two adjacent
responsibilities it deliberately does not reimplement:

| Responsibility | Who owns it | Notes |
|---|---|---|
| Executing a bioinformatics workflow | Not this project (e.g. Nextflow, Snakemake, or any other engine, run by the user) | Out of scope entirely |
| Capturing workflow-run provenance for Nextflow pipelines | **nf-prov** (external Nextflow plugin) | Existing functionality; this project only optionally *consumes* its RO-Crate output |
| RO-Crate reading/writing (JSON-LD serialization) | **ro-crate-py** (external library) | Existing functionality; this project depends on it rather than reimplementing RO-Crate serialization |
| Manifest validation against explicit rules | **This project** | Novel |
| Validation report generation (JSON/Markdown) | **This project** | Novel |
| Enrichment of an RO-Crate (own or nf-prov-produced) with validated metadata | **This project** | Novel |

Keeping this table accurate is more important than keeping any individual
component diagram accurate — it is the answer to "did we build this, or
are we standing on something that already exists?"

## 2. Component overview

```
                    ┌───────────────────────────┐
                    │        CLI (Typer)         │
                    │  entry point, arg parsing, │
                    │  exit codes                │
                    └──────────────┬─────────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 ▼                                   ▼
     ┌───────────────────────┐          ┌─────────────────────────────┐
     │   Manifest parsing     │          │  RO-Crate input (optional)  │
     │   (PyYAML → dict →     │          │  existing nf-prov crate,    │
     │   Pydantic models)     │          │  read via ro-crate-py       │
     └───────────┬────────────┘          └──────────────┬───────────────┘
                 │                                       │
                 ▼                                       │
     ┌───────────────────────┐                           │
     │   Generic run model    │◄──────────────────────────┘ (future: map
     │   (docs/data-model.md) │                                crate terms
     │   + modality profiles  │                                onto model)
     └───────────┬────────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │   Validation engine    │
     │   core rules + profile │
     │   rules, each with a   │
     │   stable rule ID       │
     └───────────┬────────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │   Findings             │
     │   (ERROR/WARNING/INFO) │
     └───────────┬────────────┘
                 │
        ┌─────────┴─────────┐
        ▼                   ▼
┌───────────────┐   ┌───────────────────────────┐
│ JSON report     │   │ Markdown report            │
└───────────────┘   └───────────────────────────┘
                 │
                 ▼
     ┌───────────────────────────┐
     │  RO-Crate generation /     │
     │  enrichment (ro-crate-py,  │
     │  RO-Crate 1.2 — see        │
     │  ADR-0002)                 │
     └───────────────────────────┘
```

## 3. Components

### 3.1 CLI layer

- Implemented with Typer.
- Responsible only for argument parsing, wiring components together, and
  translating findings/errors into process exit codes. It must not contain
  validation logic itself (per the "keep parsing, validation, reporting and
  RO-Crate generation separate" architecture rule in `CLAUDE.md`).
- Exit code convention (proposed, to be confirmed during implementation):
  `0` = no ERROR findings, `1` = at least one ERROR finding, `2` = the tool
  itself failed to run (for example, malformed YAML that cannot be parsed
  at all).

### 3.2 Manifest parsing

- Reads a YAML run manifest from disk using PyYAML.
- Converts the raw YAML structure into typed Pydantic models representing
  the generic run model (see `docs/data-model.md`).
- Parsing failures (malformed YAML, missing required structural fields)
  are distinguished from validation failures (structurally valid manifest
  that fails a rule). Parsing failures should stop the pipeline early;
  validation failures should be collected as findings.

### 3.3 Generic run model and modality profiles

- The core data model is deliberately modality-agnostic: it describes a
  run, its inputs, its parameters, its outputs, and its provenance, without
  assuming sequencing, imaging, or any other specific technique.
- Modality-specific structure and rules are added through optional
  **profiles**, which extend the core model and/or contribute additional
  validation rules. Profiles are additive: the core model and core rules
  must remain valid and independently useful with no profile applied.
- See `docs/data-model.md` for the model itself and ADR-0003 for the
  design rationale of the profile mechanism.

### 3.4 Validation engine

- Applies rules to the parsed model. Each rule has a stable, versioned
  identifier (for example, a short code plus number) so that a finding can
  be traced back to exactly one rule, referenced externally (e.g. in an
  audit record or a suppression list), and have its severity or wording
  changed over time without breaking that traceability.
- Produces a list of findings, each with: rule ID, severity
  (ERROR/WARNING/INFO), a human-readable message, and a reference to the
  location in the manifest the finding applies to.
- Must not require network access. Any rule that would require network
  access (for example, an ontology-term lookup) is explicitly out of scope
  for Milestone 0 (see non-goals in `docs/project-charter.md`) and, if
  ever added later, would need to be optional and clearly separated.

### 3.5 Reporting

- Serializes findings to JSON (machine-readable, stable schema) and to
  Markdown (human-readable summary).
- Report generation is a pure function of the findings list plus run
  metadata — it does not re-run validation or re-read the manifest.

### 3.6 RO-Crate generation and enrichment

- Uses `ro-crate-py` to create a new RO-Crate package (targeting RO-Crate
  1.2; see ADR-0002) describing the run, or to open and enrich an existing
  crate.
- Two input paths are anticipated:
  1. **Fresh generation** — build a new RO-Crate from the validated
     manifest and its outputs.
  2. **Enrichment of an existing nf-prov crate** — accept a crate already
     produced by nf-prov for a Nextflow run, and add validated metadata to
     it (for example, findings, additional descriptive metadata) without
     discarding what nf-prov already captured. This is explicitly listed
     as optional/future-facing in the MVP scope ("optionally accept an
     existing nf-prov RO-Crate for future enrichment") and is one of the
     least-defined parts of the design — see open questions below.

## 4. Data flow summary

1. User provides a YAML manifest (and, optionally, an existing nf-prov
   RO-Crate) on the command line.
2. The manifest is parsed into the generic run model, with any applicable
   profile(s) applied.
3. The validation engine runs core rules and any profile rules, producing
   findings.
4. Findings are serialized to JSON and Markdown reports.
5. An RO-Crate is created or, if an existing crate was supplied, enriched.

## 5. Cross-cutting concerns

- **Determinism.** Given the same manifest, configuration, and profile
  set, output (reports and crate contents) should be reproducible. Where
  this is not practically achievable (for example, timestamps that must
  reflect the actual run time), this should be documented per-field rather
  than silently accepted.
- **No silent mutation.** The tool must not alter the user's source
  manifest file. Any normalization happens on an in-memory or output copy.
- **Testability.** Each component in section 3 should be testable in
  isolation using synthetic fixtures, consistent with the separation-of-
  concerns rule.

## 6. Open questions

- Exact CLI command/subcommand structure (single command with flags vs.
  subcommands for validate/report/package) is not yet decided.
- The precise mechanism for mapping/merging validated metadata into an
  existing nf-prov RO-Crate (which JSON-LD entities to add or update, how
  to avoid conflicting with nf-prov-owned entities) is not yet designed and
  should be resolved before enrichment is implemented, ideally informed by
  reading nf-prov's actual current output against a synthetic Nextflow run.
- Whether profiles are implemented as a Python plugin/entry-point mechanism
  or as a simpler internal registry is not yet decided (see ADR-0003 for
  the current thinking).
- Exit code and logging conventions above are proposals, not settled
  decisions.
