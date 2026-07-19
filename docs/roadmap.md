# Roadmap — Bio Run Crate

**Status:** Planning document. This is an open-source, volunteer-driven
project; nothing on this page is a commitment or a date-based promise.
Horizons are ordered ("current", "next", "later") rather than scheduled.
Items beyond Milestone 0 are speculative and intended to prompt discussion,
not to lock in design decisions ahead of the ADRs that would actually need
to be written for them.

## Current — Milestone 0

Establish the repository, documentation, data model, and a minimal working
CLI, using entirely synthetic examples. Defined in `CLAUDE.md`.

Scope (see `docs/project-charter.md` §3 for the authoritative list):

- [ ] Generic run model implemented as typed Pydantic models
      (`docs/data-model.md` Part A).
- [ ] YAML manifest parsing.
- [ ] Core validation rule engine with stable rule IDs.
- [ ] ERROR/WARNING/INFO findings.
- [ ] JSON and Markdown report generation.
- [ ] RO-Crate 1.2 package creation via `ro-crate-py`.
- [ ] Minimal CLI (Typer) wiring the above together.
- [ ] Test suite covering parsing, validation, and reporting with synthetic
      fixtures.
- [ ] This documentation set, kept accurate as implementation proceeds.

Explicitly **not** in Milestone 0 (see non-goals in
`docs/project-charter.md`): any LIMS/ELN integration, any catalog
integration, cloud access, automatic ontology lookup, a web interface,
LLM-based generation, real data of any kind.

## Next (candidate, not committed)

These would each need their own design discussion and likely their own ADR
before work starts:

- **RO-Crate enrichment of an existing nf-prov crate.** Listed as
  "optional... for future enrichment" in the MVP scope. Needs a concrete
  design for how validated metadata is merged into a crate this project
  did not create, without conflicting with nf-prov-owned entities (see
  `docs/architecture.md` §6).
- **First modality profile, implemented (not just illustrative).** Turning
  one of the illustrative profiles in `docs/data-model.md` Part B into a
  real, tested profile — likely sequencing, since it is the most commonly
  requested modality in comparable tooling, though this has not been
  confirmed by any survey of prospective users.
- **Packaging and distribution** (e.g. publishing to a package index) once
  the CLI is stable enough to be useful to others.
- **Contribution process formalization** — issue templates, a
  `CONTRIBUTING.md`, and resolution of the open licensing question in
  `docs/project-charter.md`.

## Later (speculative)

- Additional modality profiles beyond the first.
- A plugin/entry-point mechanism for third-party profiles, if the internal
  registry approach in ADR-0003 turns out to be too limiting.
- Batch/multi-run manifest support (see open question in
  `docs/data-model.md` §A.7).
- Any optional, clearly-separated network-dependent feature (for example,
  ontology-term lookup) — only if there is real demand, since it would
  contradict a current design principle (no network dependency for core
  functionality) and would need to remain fully optional.

## Explicitly not planned

Carried forward from the non-goals list and repeated here so the roadmap
doesn't silently drift toward them: LIMS/ELN integration, data-catalog
integration, cloud access, a web interface, LLM-based metadata generation,
and handling of real patient, research, or organizational data. Any change
to this list should happen through an explicit ADR, not through roadmap
edits alone.

## Open questions

- No target dates exist for any horizon beyond "current." Whether this
  project will ever adopt date-based milestones depends on whether it
  gains enough contributors to make that meaningful.
- The "Next" section is an editorial guess at priority order based on what
  the MVP scope explicitly flags as future work (item 6, nf-prov
  enrichment) versus what is only implied (profiles, packaging). It has
  not been validated with any user or contributor survey.
