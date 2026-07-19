## Problem

The project's security and privacy rules forbid committing credentials, API
keys, tokens, private URLs, or personal email addresses. Manual review cannot
reliably catch these. Automated secret scanning in CI provides a safety net that
blocks accidental leakage before it reaches the default branch, reinforcing the
"synthetic and public-safe only" guarantee.

## Scope

- Add automated secret scanning that runs in CI on push and pull request.
- Configure it to detect common credential and key patterns and fail the build
  on a finding.
- Provide an allowlist mechanism for known-safe synthetic placeholders (e.g.
  `.env.example`, `example.org` values) to avoid false positives.
- Document how to run the scan locally and how to handle a finding.

## Out of scope

- The general CI check workflow for tests/lint/type (separate issue).
- Runtime secret management or vaulting.
- Scanning of anything outside this repository.

## Acceptance criteria

- [ ] Secret scanning runs in CI and fails the build on a detected secret.
- [ ] Synthetic placeholders are allowlisted so example files do not trigger false positives.
- [ ] Local usage and finding-remediation steps are documented.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes
