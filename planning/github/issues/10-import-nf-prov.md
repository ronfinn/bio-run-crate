## Problem

Pipelines run with Nextflow can already emit provenance as an RO-Crate via
nf-prov. Rather than reimplement provenance capture, Bio Run Crate should be able
to accept such a crate as input and preserve it faithfully, laying the
groundwork for a future enrichment step. The immediate need is safe ingestion:
reading an existing crate without corrupting or overwriting nf-prov-owned
entities.

## Scope

- Accept the path to an existing nf-prov-produced RO-Crate as optional input.
- Read and validate that the crate is well-formed and preserve its existing
  entities unchanged.
- Establish where validated Bio Run Crate metadata would later attach, without
  yet mutating nf-prov-owned entities.
- Use only a synthetic, hand-authored example crate for tests.

## Out of scope

- The actual enrichment/merge of validated metadata into the crate (future
  work; this issue only imports and preserves).
- Any Nextflow execution or nf-prov plugin invocation.
- Network access or fetching remote crates.

## Acceptance criteria

- [ ] An existing nf-prov crate can be supplied and is read without modification.
- [ ] The importer preserves nf-prov-owned entities and reports on the crate's contents.
- [ ] A synthetic example nf-prov crate is used for testing.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes
