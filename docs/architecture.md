# Architecture — Bio Run Crate

**Status:** Partly implemented for Milestone 0. Manifest parsing
(`src/bio_run_crate/manifest.py`), the generic run model (`models.py`), the
structured findings model (`findings.py`) and the core validation engine
(`validation/`) all exist and are wired into the `validate` CLI command; report
generation and RO-Crate output are still target design. This document should be updated to reflect reality as components are
built, per the workflow rule in `CLAUDE.md` ("update documentation when
behaviour changes").

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
- Exit code convention (**settled and implemented**):

  | Code | Meaning |
  |---|---|
  | `0` | The manifest parsed and validation produced no ERROR findings. WARNING and INFO findings alone do not change this. |
  | `1` | The manifest parsed, but validation produced at least one ERROR finding. |
  | `2` | The manifest never reached the rule engine: it was missing or unreadable, was not valid YAML, had a non-mapping top level, or failed Pydantic's structural/schema validation. |

  The `1`/`2` split follows the boundary in §3.2: `1` means "we validated your
  manifest and it has an error", `2` means "there was nothing to validate".
  Structural failures are reported as Pydantic's own errors and are deliberately
  *not* dressed up as `CORE-*` findings, since they are not rule findings.
- Presentation of findings is the CLI's own concern: `validate` renders them as a
  terminal table (rule ID, severity, location, message) on stderr, with a
  one-line summary on stdout. `validate --format json` instead emits the
  reusable JSON report (§3.5) on stdout and suppresses both, without changing
  which rules run or which exit code is returned. The Markdown reporter is not
  yet built.

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

**Status:** implemented for the core rule set, in `src/bio_run_crate/validation/`
(`rule.py` — what a rule is; `registry.py` — a rule set and its identifier
invariants; `core_rules.py` — the deliberately minimal core rule set, listed in
`docs/data-model.md` §A.8.2; `engine.py` — `validate_manifest()`, the single
public entry point). Profile rule sets are not implemented.

- Applies rules to the parsed model. Each rule has a stable, versioned
  identifier (`<NAMESPACE>-<NNN>`, e.g. `CORE-001`; the convention is defined in
  `docs/data-model.md` §A.8.1, whose syntax the `Finding` model validates) so
  that a finding can be traced back to exactly one rule, referenced externally
  (e.g. in an audit record or a suppression list), and have its severity or
  wording changed over time without breaking that traceability.
- Runs every rule in the registry and collects their findings; a rule that
  produces findings never prevents later rules from running, so one invocation
  reports everything wrong with a manifest. Rule identifiers are unique by
  construction — the registry rejects a duplicate, and can pin the namespace its
  rules must use — and retired identifiers are recorded explicitly so they cannot
  be reused (`docs/data-model.md` §A.8.1). Each rule emits exactly one declared
  severity, which the engine enforces, so severity is a stable property of the
  rule ID.
- Produces findings, each with: rule ID, severity (ERROR/WARNING/INFO), a
  human-readable message, and a `Location` referring to the place in the
  manifest the finding applies to. Findings are aggregated into a
  `ValidationResult`, which canonically orders them on every construction path,
  so the engine's emission order cannot leak into reports.
- Must not require network access. Any rule that would require network
  access (for example, an ontology-term lookup) is explicitly out of scope
  for Milestone 0 (see non-goals in `docs/project-charter.md`) and, if
  ever added later, would need to be optional and clearly separated.

### 3.5 Reporting

**Status:** the JSON report is implemented, in `src/bio_run_crate/reporting/`
(`json_report.py`). The Markdown report is **not implemented**.

- Serializes findings to JSON (machine-readable, stable schema) and to
  Markdown (human-readable summary).
- Report generation is a pure function of the findings list plus run
  metadata — a reporter is a pure consumer of an already-parsed `RunManifest`
  and the `ValidationResult` produced for it. It does not re-run validation,
  re-read the manifest, mutate either input, read the clock, or use the network.
- **JSON report.** A versioned document (`schema_version`, currently `"1"`)
  carrying the run identifier, a per-severity summary that always includes all
  three severities, and every finding with its rule ID, severity, message and
  structured `location`. Serialization is deterministic by contract — fixed key
  order, canonical finding order, fixed formatting, one trailing newline, no
  terminal styling — so reports are diffable across runs. Reachable as
  `validate MANIFEST --format json`, which emits exactly one document on stdout
  and suppresses the terminal table and summary; exit codes are unchanged. A
  manifest that fails structurally never reaches the rule engine, so there is no
  `ValidationResult` and no report is produced — it keeps its existing stderr
  diagnostics and exit code `2`. The full schema and its contracts are
  documented in `docs/json-report.md`.
- **Markdown report** — pending (issue #8). It will consume the same two inputs.

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
- Logging conventions are not yet settled. (The exit-code convention in §3.1 is
  now settled and implemented.)
