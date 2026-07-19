## Problem

A new user needs a guided, end-to-end path from installation to a validated run
and a generated crate. The reference docs describe components in isolation, but
there is no single walkthrough that a beginner can follow start to finish. A
tutorial lowers the barrier to adoption and doubles as living documentation that
must stay accurate as behaviour changes.

## Scope

- Write a beginner tutorial covering: installing with `uv`, running the CLI,
  validating a synthetic manifest, reading the JSON and Markdown reports, and
  generating a minimal RO-Crate.
- Use only the repository's synthetic example manifests.
- Show expected output and exit statuses for both a valid and an invalid
  manifest.
- Link the tutorial from the README and docs index.

## Out of scope

- Advanced topics: modality profiles, nf-prov import, or contributor workflow.
- Any feature not yet implemented at the time of writing (the tutorial covers
  shipped behaviour only).
- Screenshots or hosted assets.

## Acceptance criteria

- [ ] A tutorial walks a beginner from install through validation, reports, and crate generation.
- [ ] It uses only synthetic examples and shows expected output for valid and invalid runs.
- [ ] It is linked from the README and stays consistent with current behaviour.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes
