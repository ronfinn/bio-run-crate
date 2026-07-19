## Problem

The core user-facing action is: point the tool at a YAML manifest and learn
whether it is valid. This issue wires parsing, the `RunManifest` model, and the
findings model together behind the `validate` command so that a manifest is
read, structurally validated, and checked against the core rule set, producing
findings and an appropriate exit status. This must work entirely offline.

## Scope

- Implement YAML manifest parsing into the `RunManifest` model using PyYAML.
- Implement the core (modality-agnostic) validation rules, each with a stable
  rule ID, emitting `Finding` objects.
- Wire the `validate` CLI command to parse, validate, and collect findings.
- Set a non-zero exit status when any ERROR-severity finding is present.
- Keep validation deterministic and network-free.

## Out of scope

- JSON and Markdown report rendering (separate issues; this issue produces the
  findings they render).
- Modality-specific profile rules (separate issue).
- RO-Crate generation.
- Any silent modification of the input manifest.

## Acceptance criteria

- [ ] `validate` parses a YAML manifest and runs the core rule set offline.
- [ ] ERROR findings cause a non-zero exit status; clean manifests exit zero.
- [ ] Each core rule has a stable identifier and emits structured findings.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes
