# Security Policy

Bio Run Crate is early-stage (alpha) software. This policy explains which
versions receive security fixes and how to report a vulnerability responsibly.

It complements the project's broader
[security and privacy policy](docs/security-and-privacy.md), which covers the
synthetic-data rule, the no-secrets rule, and the tool's threat model.

## Supported versions

The project is pre-1.0 and evolving. Only the latest released version and the
current `main` branch receive security fixes. Older `0.x` versions are not
maintained.

| Version | Supported |
|---------|-----------|
| latest `0.x` / `main` | ✅ |
| any earlier version   | ❌ |

## Reporting a vulnerability

**Please do not report security vulnerabilities through public issues, pull
requests, or discussions.**

Instead, report privately through the repository's security-advisory mechanism
(on GitHub, "Security" → "Report a vulnerability", which opens a private
advisory visible only to the maintainers). If a private channel is unavailable
to you, open a minimal public issue that says only that you have found a
security problem and asks a maintainer to contact you privately — do not include
any details in that issue.

When you report, please include where practical:

- a description of the issue and its potential impact;
- the version, commit, or branch affected;
- steps to reproduce, ideally with a **synthetic** manifest or input (never
  include real data, credentials, or private identifiers in a report);
- any suggested remediation.

## What to expect

- We aim to acknowledge a report within a few days.
- We will confirm the issue, keep you informed of progress, and credit you in
  the changelog if you wish once a fix is released.
- Please give us reasonable time to release a fix before any public disclosure.

## Scope

Bio Run Crate's core path reads a local YAML manifest and validates it offline.
Points of particular interest for security review:

- **Untrusted input.** Manifests (and, when implemented, any RO-Crate supplied
  for enrichment) are untrusted input. YAML is parsed with safe loading, not
  arbitrary object deserialization.
- **No secrets, no network for core validation.** Core validation requires no
  credentials and no network access. Reports of accidental network calls,
  credential handling, or secret leakage in output are in scope.
- **No real data in the repository.** All examples, fixtures, and documentation
  use synthetic, `example.org`-style values. A report that real data,
  credentials, or private identifiers have entered the repository is in scope.

Features described as planned in the [README](README.md) and
[architecture](docs/architecture.md) (structured findings, JSON/Markdown
reports, RO-Crate output, nf-prov enrichment, modality profiles) are not yet
implemented; vulnerability reports should target behaviour that exists today.
