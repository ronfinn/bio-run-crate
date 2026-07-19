# ADR-0003: Profile-based validation for modality-specific rules

## Status

Accepted (Milestone 0 design; mechanism not yet implemented)

## Context

`CLAUDE.md` states an explicit architecture rule: "Modality-specific rules
must be implemented as profiles or extensions." The core run model and
core rule set (`docs/data-model.md` Part A) are deliberately modality-
agnostic. But real analysis runs — sequencing, imaging, mass spectrometry,
and others — have modality-specific metadata that a general-purpose core
model should not have to encode, and modality-specific correctness checks
that should not silently apply (or silently fail to apply) to runs of a
different modality.

Without a defined extension mechanism, there is a risk that modality-
specific fields and rules get added directly to the core model over time,
which would violate the separation-of-concerns principle in
`docs/architecture.md` and make the core harder to reason about and test
in isolation.

Note: this ADR concerns this project's own internal validation-profile
concept. It is unrelated to the idea of an RO-Crate specification
"profile" mentioned as an open question in ADR-0002 — the two uses of the
word "profile" refer to different things and should not be conflated.

## Decision

Introduce a **profile** concept: an optional, named unit that can:

1. extend the core data model with additional fields (typically attached
   to `Artifact` entries or `Analysis.parameters`, per
   `docs/data-model.md` Part B), and/or
2. contribute additional validation rules, each with a rule-ID prefix
   distinct from the core rule set (for example, core rules as `CORE-###`
   and a given profile's rules as `<PROFILE>-###`), and/or
3. leave both alone and simply document expected conventions, if a
   modality needs no additional structure beyond the core model.

A manifest declares zero or more profiles to apply (see the `profile`
field in `docs/data-model.md` §A.1). With no profile declared, only the
core model and core rules apply, and the tool remains fully useful.

The concrete mechanism for how profiles are registered and loaded
(entry-point/plugin discovery vs. a simple internal registry mapping
profile name to a Python object) is **not** decided by this ADR — see open
questions below. This ADR fixes the *concept* (profiles are optional,
additive, and separately identified), not the *implementation
mechanism*.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| **Encode all modality-specific fields and rules directly in the core model, with conditional logic** | Directly contradicts the `CLAUDE.md` architecture rule and the separation-of-concerns principle; would make the core model's required/optional fields depend on which modality a run belongs to, undermining "modality-agnostic core." |
| **One separate, unrelated tool per modality** | Would duplicate the parsing/reporting/RO-Crate-generation machinery per modality instead of sharing it, contradicting the goal of a single general-purpose tool. |
| **No modality-specific support at all (core rules only, forever)** | Simplest option, but does not meet the MVP's stated intent that modality-specific rules should be supportable "as profiles or extensions" — this alternative would mean never building that extensibility, which was rejected as too limiting for the project's stated purpose. |

## Consequences

- Core validation logic must be written and tested without ever assuming
  a profile is present.
- Any profile's fields/rules must be additive: applying a profile must
  never make a manifest that was valid under the core rules alone become
  structurally rejected before profile-specific validation even runs.
- Rule-ID namespacing (core vs. per-profile prefixes) needs to be
  established early, since rule IDs are meant to be stable and externally
  referenceable (`docs/data-model.md` §A.6, `docs/security-and-privacy.md`
  §4); retrofitting namespacing later would be a breaking change to any
  external reference to a rule ID.
- Illustrative profiles in `docs/data-model.md` Part B (sequencing,
  imaging, mass spectrometry) are placeholders for this mechanism, not
  commitments to build those three first — see `docs/roadmap.md`.

## Open questions / verification needed

- Whether profiles are implemented as Python entry-point plugins
  (discoverable from separately installed packages) or as a simple
  internal registry within this repository. The entry-point approach
  scales better to third-party profiles but adds packaging complexity;
  the internal-registry approach is simpler for Milestone 0 but would need
  a migration path later if third-party profiles become desirable.
- How conflicts are resolved if more than one declared profile defines the
  same field or rule ID differently — not yet designed.
- Whether profile field sets should be grounded in existing published
  minimal-information checklists or community conventions for each
  modality (rather than the placeholder fields shown in
  `docs/data-model.md` Part B), which would require dedicated research
  before the first real profile is implemented, not assumption from
  general knowledge.
- Versioning of a profile independent of the core tool's version has not
  been designed.
