# Project Charter — Bio Run Crate

**Status:** Draft, Milestone 0
**Audience:** Contributors, maintainers, and prospective adopters
**Scope note:** This charter describes an open-source, general-purpose tool.
It does not reference any specific organization, employer, deployment, or
proprietary system. All examples referenced elsewhere in the documentation
set are synthetic.

## 1. Purpose

Bio Run Crate is a general-purpose, standalone command-line tool that:

1. Validates biological analysis-run metadata against explicit, versioned
   rules.
2. Produces structured, machine-readable and human-readable validation
   reports.
3. Creates or enriches [RO-Crate](https://www.researchobject.org/ro-crate/)
   packages describing an analysis run and its outputs.

The tool is intended to help teams that produce computational biology
results (of any modality — sequencing, imaging, mass spectrometry, and
others) attach consistent, checkable metadata to those results, independent
of which laboratory information system, electronic lab notebook, or
workflow engine produced them.

Bio Run Crate is a metadata-validation and packaging utility. It is not a
laboratory information management system (LIMS), not a workflow engine, and
not a data catalog.

## 2. Problem statement

Analysis-run metadata is frequently inconsistent, incomplete, or captured in
ad hoc formats that differ from team to team and modality to modality. This
makes it difficult to:

- Confirm that a run's metadata is complete enough to be trusted before
  results are used downstream.
- Package a run's inputs, parameters, and outputs in a portable,
  standards-based format suitable for archiving or sharing.
- Apply consistent, auditable checks across many runs at scale.

Bio Run Crate addresses the metadata-validation and packaging layer of this
problem. It does not address instrument integration, sample tracking, or
long-term storage.

## 3. Goals (Milestone 0 / MVP)

As defined in the project's working instructions (`CLAUDE.md`), the MVP
must:

1. Read a YAML run manifest.
2. Validate it using explicit Python models and rules.
3. Return findings at ERROR, WARNING, and INFO severity.
4. Produce both JSON and Markdown validation reports.
5. Create an RO-Crate 1.2 package using `ro-crate-py`.
6. Optionally accept an existing [nf-prov](https://github.com/nextflow-io/nf-prov)
   RO-Crate as input, for future enrichment.
7. Use only synthetic and public-safe example data throughout the
   repository, documentation, and tests.

## 4. Explicit non-goals

The project does **not** currently implement, and Milestone 0 does not plan
for:

- Integration with any specific electronic lab notebook or LIMS product
  (for example, Benchling-style systems).
- Integration with any specific data catalog or metadata platform (for
  example, DataHub- or OpenMetadata-style systems).
- Cloud storage or cloud compute access of any kind.
- Automatic ontology lookup or term resolution against external services.
- A web interface or hosted service.
- LLM-based or otherwise generative metadata creation.
- Handling of real patient data, real research data, or any proprietary or
  organization-specific system.

These are recorded as non-goals rather than omissions so that scope
decisions are traceable. Any future change to this list should go through
an ADR (see `docs/decisions/`).

## 5. Design principles

These principles are carried through into `docs/architecture.md` and the
ADRs:

- **Separation of concerns.** Parsing, validation, reporting, and RO-Crate
  generation are kept as distinct components with narrow interfaces.
- **Stable, addressable rules.** Every validation rule has a stable
  identifier so that findings can be tracked, suppressed, or referenced in
  external audit records.
- **No network dependency for core validation.** Reading a manifest and
  validating it must work offline. Any feature that requires network access
  (for example, optional ontology lookups, if ever added) must be
  clearly separated and optional.
- **Modality-agnostic core, pluggable modality profiles.** The core data
  model and core rule set do not assume any single experimental modality.
  Modality-specific behavior is added through optional profiles (see
  `docs/data-model.md`).
- **No silent mutation.** The tool does not rewrite or "fix" user input
  without an explicit, visible action.
- **Deterministic output.** Given the same input and configuration, the
  tool should produce the same report and the same crate contents, so that
  output is diffable and auditable.
- **Synthetic data everywhere in the project itself.** All examples,
  fixtures, and documentation samples use invented identifiers,
  `example.org`-style domains, and clearly synthetic values.

## 6. Relationship to existing tools

Bio Run Crate is designed to complement, not replace, existing provenance
tooling:

- **nf-prov** (a Nextflow plugin) already produces provenance output,
  optionally as an RO-Crate, for pipelines run with Nextflow. Bio Run Crate
  treats an nf-prov-produced RO-Crate as one possible *input* that a future
  enrichment step may extend with additional validated metadata. Bio Run
  Crate does not reimplement or replace nf-prov's provenance capture.
- **ro-crate-py** is the library this project uses to read and write
  RO-Crate packages. Bio Run Crate does not implement its own RO-Crate
  serialization.

See `docs/architecture.md` for how these boundaries map onto components,
and ADR-0002 for the RO-Crate version decision.

## 7. Stakeholders and roles (project-level, not organizational)

- **Maintainers** — responsible for architecture decisions (recorded as
  ADRs), release management, and review standards.
- **Contributors** — anyone submitting issues, documentation, or code
  changes.
- **Adopters** — teams or individuals who run the tool against their own
  (non-synthetic, out-of-repository) data. The project has no visibility
  into and makes no claims about adopters' data.

## 8. Success criteria for Milestone 0

- A minimal CLI exists that can read a synthetic YAML manifest, run
  validation, and emit both JSON and Markdown reports.
- An RO-Crate 1.2 package can be created from a synthetic run.
- The documentation set listed in `docs/` accurately describes the current
  state of the project and clearly labels anything aspirational as such.
- All checks defined in `CLAUDE.md` (tests, lint, format, type-check) pass.

## 9. Open questions

- **Licensing.** No `LICENSE` file currently exists in the repository. The
  choice of open-source license (and whether contributor sign-off such as a
  DCO or CLA is required) has not yet been decided and should be resolved
  before the project accepts external contributions.
- **Governance model beyond Milestone 0.** This charter describes
  Milestone 0 governance informally (maintainers/contributors/adopters). A
  more formal governance model (for example, how maintainers are added,
  how ADRs are approved) is not yet defined.
- **Versioning and release policy.** Not yet defined; should be addressed
  once the MVP is functional.
- **Long-term relationship with nf-prov.** Whether enrichment should
  eventually be contributed upstream to nf-prov, remain a downstream
  post-processing step, or both, is undecided and out of scope for
  Milestone 0.
