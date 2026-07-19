# Security and Privacy — Bio Run Crate

**Status:** Policy document for Milestone 0 onward. This expands the
security and privacy rules already stated in `CLAUDE.md` into a fuller
policy for contributors and reviewers. Where this document adds detail
beyond `CLAUDE.md`, that detail is this project's interpretation, not an
external requirement, unless a source is cited.

## 1. Principles

- **Synthetic data only, inside the repository.** All example manifests,
  fixtures, test data, and documentation samples must use invented
  identifiers, invented values, and `example.org`-style placeholders. Real
  sample IDs, real instrument serial numbers, real internal system names,
  and real organization names must never appear in this repository.
- **No credentials in the repository.** No real API keys, access tokens,
  passwords, private URLs, or private registry paths, ever, including in
  examples, tests, comments, or commit messages.
- **Core functionality requires no credentials and no network access.**
  Reading a manifest and validating it against core (and profile) rules
  must work fully offline. This is both a privacy property (nothing is
  sent anywhere) and a reliability property.
- **No inspection of secret material.** Contributors and any automated
  tooling working in this repository must never open, display, or log the
  contents of `.env`, credential files, private keys, or token files. The
  repository's `.gitignore` already excludes these; this rule extends that
  intent to how the project is worked on, not just what is committed.
- **No data from outside the repository.** Tooling and contributors
  working on this project should not read files outside the repository
  boundary as part of normal project work.
- **Personal information.** Anything that may reveal a personal email
  address or other personally identifying information — in examples,
  fixtures, or generated output — should be flagged and replaced with a
  synthetic placeholder before merging.

## 2. Data classification

| Category | Allowed in this repository? |
|---|---|
| Synthetic manifests, fixtures, and example RO-Crates | Yes — required to be synthetic |
| Real biological/clinical/research data of any kind | No |
| Real organizational identifiers (systems, buckets, internal URLs) | No |
| Real personal names/emails, except public contributor attribution (e.g. commit authorship) | No, outside of standard contributor attribution |
| Placeholder credentials clearly marked as non-functional (e.g. `.env.example`) | Yes, if clearly non-functional and documented |

This table applies to the project's own repository. It says nothing about
how an adopter should classify or handle *their own* data when they run
the tool — that is the adopter's responsibility and depends on their own
regulatory and organizational context, which this project has no
visibility into.

## 3. Threat model (for the tool itself)

Bio Run Crate's core validation and reporting path is designed to run
offline, against local files, producing local output. Within that scope:

- **Input trust.** The manifest and any RO-Crate supplied for enrichment
  are user-supplied input. Parsing must not execute arbitrary code from
  the manifest (for example, YAML parsing must use safe loading, not
  arbitrary object deserialization).
- **Output trust.** Generated reports and RO-Crates should not embed
  anything from the environment that the user did not explicitly provide
  or that isn't necessary for the crate to be valid (for example, avoid
  leaking local absolute file-system paths from the machine running the
  tool into a shared/portable crate — use relative paths where the
  RO-Crate model allows it).
- **Supply chain.** Dependencies are pinned via `uv.lock`. Any dependency
  addition or upgrade should be a deliberate, reviewed change, since this
  tool may be run in environments where dependency provenance matters.
- **Extension points (profiles, and any future enrichment of externally
  supplied crates).** Because profiles and crate-enrichment logic process
  externally supplied structured data (an RO-Crate produced by another
  tool, in the enrichment case), they should be reviewed with the same
  "don't execute untrusted content" mindset as manifest parsing.

Formal threat-modeling beyond this outline (for example, a structured
STRIDE-style pass) has not been done and is listed as an open question
below.

## 4. Audit readiness

This project is designed to make its output usable as part of an
adopter's own audit trail:

- **Deterministic output where practical**, so that a given manifest and
  configuration reproducibly produce the same report and crate contents,
  making changes over time diffable.
- **Stable rule identifiers**, so a finding can be referenced externally
  (for example, in a change record or exception log) and remain
  meaningful even if the rule's wording changes later.
- **Separation of validation from mutation.** The tool does not silently
  alter the user's source manifest. Anything the tool changes (e.g. an
  enriched crate) is a distinct output artifact.

These properties support audit readiness; they do not by themselves
constitute compliance with any specific regulatory framework. This project
makes no claims about compliance with any named standard or regulation —
any such claim would need to be verified against the specific framework in
question and is out of scope here.

## 5. Contributor guidelines

Before opening a pull request, contributors should confirm:

- No real identifiers, credentials, or personal data were introduced,
  including in test fixtures and generated example output.
- Any new example manifest or crate is clearly synthetic and uses
  `example.org`-style placeholders.
- Any new dependency is justified and reviewed, not just "it worked
  locally."
- Any change that affects what data the tool reads, writes, or transmits
  is called out explicitly in the pull request description.

## 6. Open questions

- Whether the project should adopt a formal vulnerability-disclosure
  process (for example, a `SECURITY.md` with a reporting contact) — not
  yet defined.
- Whether a license and contributor agreement are required before external
  contributions are accepted (tracked in `docs/project-charter.md` as
  well).
- Whether any future optional network-dependent feature (for example,
  ontology lookups, explicitly a non-goal today) would need its own
  privacy review before being added — deferred until such a feature is
  actually proposed.
- Whether a structured threat-modeling exercise (beyond the outline in
  §3) is warranted once the enrichment-of-external-crates feature is
  designed in detail.
