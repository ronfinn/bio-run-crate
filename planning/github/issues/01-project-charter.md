## Problem

Bio Run Crate needs an authoritative, version-controlled statement of what it
is, what it does, and — just as importantly — what it deliberately does not do.
Without a written charter and an explicit non-goals list, scope decisions are
untraceable and the project risks drifting toward integrations and features
(LIMS/ELN, data catalogs, cloud, LLM generation) that Milestone 0 explicitly
excludes. Contributors and adopters need a single reference that describes the
purpose, design principles, and success criteria for the MVP.

## Scope

- Maintain `docs/project-charter.md` covering purpose, problem statement,
  Milestone 0 goals, explicit non-goals, design principles, relationship to
  existing tools (nf-prov, ro-crate-py), stakeholder roles, and success
  criteria.
- Keep the non-goals list aligned with `CLAUDE.md` and cross-referenced from
  `docs/roadmap.md`.
- Record that any change to the non-goals list must go through an ADR.
- Ensure all examples referenced remain synthetic and organisation-neutral.

## Out of scope

- Choosing an open-source licence (tracked as an open question).
- Defining a formal post-Milestone-0 governance model.
- Versioning and release policy detail beyond naming the v0.1.0 target.
- Any code changes.

## Acceptance criteria

- [ ] The charter states the purpose, problem, MVP goals, and success criteria.
- [ ] The explicit non-goals list matches `CLAUDE.md` and is cross-referenced from the roadmap.
- [ ] The charter notes that non-goal changes require an ADR.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes
