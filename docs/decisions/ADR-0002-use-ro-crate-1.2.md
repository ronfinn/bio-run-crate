# ADR-0002: Target RO-Crate 1.2 via ro-crate-py

## Status

Accepted (Milestone 0), with verification items noted below that should be
confirmed before or during implementation.

## Context

The project needs a packaging format for describing an analysis run
(inputs, outputs, provenance, and — later — validation findings) that is:

- based on an existing, community-maintained specification rather than a
  project-invented format, so that output is portable and interoperable
  with other tooling;
- machine-readable (so it can be consumed programmatically) and groundable
  in linked-data conventions (so terms can, in principle, be mapped to
  external vocabularies);
- already supported by an existing Python library, consistent with
  ADR-0001's decision to build on the Python ecosystem rather than
  reimplement serialization formats.

[RO-Crate](https://www.researchobject.org/ro-crate/) — "Research Object
Crate" — is a lightweight specification for packaging research data
together with machine-readable metadata, built on schema.org and JSON-LD
conventions. It is relevant here specifically because:

- **nf-prov**, an existing Nextflow plugin, can already produce an RO-Crate
  describing a Nextflow pipeline run. Item 6 of the MVP scope
  (`docs/project-charter.md` §3) is to optionally accept such a crate as
  input for future enrichment, which requires this project to speak the
  same packaging format.
- **ro-crate-py** is an existing Python library for reading and writing
  RO-Crate packages, consistent with the Python-based toolchain in
  ADR-0001.

## Decision

Target **RO-Crate 1.2** as the packaging format for crates this project
creates or enriches, implemented via the **ro-crate-py** library
(`rocrate` package, already listed as a dependency in `pyproject.toml`).

This decision is carried over directly from the project's working
instructions (`CLAUDE.md`, MVP scope item 5), and this ADR exists to record
the reasoning and the verification work that should accompany it, rather
than to introduce a new choice.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| **A project-specific JSON/YAML metadata format** | Would be simpler to implement but would not be portable or recognizable to any other tool, and would specifically break interoperability with nf-prov-produced crates, which is a named MVP requirement. |
| **BCO (BioCompute Object)** | A specification used in some bioinformatics/regulatory contexts. Not chosen for Milestone 0 because RO-Crate's link to nf-prov's existing output is more directly relevant to this project's MVP scope; this project has not done a comparative evaluation of BCO and makes no claim about which is generally preferable. |
| **A different RO-Crate version (e.g. 1.1)** | Not adopted because the project's stated target, both in `CLAUDE.md` and in the `rocrate` dependency choice, is 1.2. Whether 1.2 vs. 1.1 is the materially correct choice is itself flagged below as something to verify, not something this ADR asserts confidently. |

## Consequences

- Crate structure, required entities, and context declarations should
  follow whatever the RO-Crate 1.2 specification actually requires —
  see verification note below.
- Enrichment of an nf-prov-produced crate (a future item, not Milestone 0)
  will need to confirm which RO-Crate version(s) nf-prov itself produces,
  since a version mismatch between what nf-prov emits and what this
  project targets could complicate merging.
- Dependence on `ro-crate-py` means this project's crate output is bounded
  by that library's feature coverage of the 1.2 specification; any gap
  becomes a constraint on this project, not something to work around by
  hand-writing JSON-LD.

## Open questions / verification needed

This project does not want to assert claims about an external standard
that have not been checked against the authoritative source. The following
should be verified against the official RO-Crate specification
(researchobject.org/ro-crate) and the `ro-crate-py` project/release notes
before this decision is treated as fully settled:

- The current official status of "RO-Crate 1.2" (published/final vs.
  draft/in-progress) at the time implementation begins, and its precise
  version identifier and specification URL.
- What, specifically, changed between RO-Crate 1.1 and 1.2, and whether
  any of those changes are load-bearing for this project's use case.
- Whether the installed version of `ro-crate-py` (pinned in `uv.lock`)
  fully supports RO-Crate 1.2, or only 1.1, or a subset of 1.2 features.
  If support is partial, this ADR's decision may need a follow-up ADR
  narrowing the target to whatever subset is actually implementable.
- Which RO-Crate version(s) nf-prov produces in its current release, since
  that determines what "accepting an existing nf-prov RO-Crate" (MVP item
  6) will actually receive as input.
- Whether this project should declare conformance to a more specific
  RO-Crate *profile* (for example, a workflow-run-oriented profile) rather
  than the base specification alone — noted here because it is directly
  relevant to nf-prov interoperability, but not decided in this ADR. See
  also ADR-0003, which is a separate decision about this project's own
  validation-profile mechanism and should not be confused with an
  RO-Crate specification profile.
