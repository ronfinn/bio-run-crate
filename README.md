# bio-run-crate

A command-line tool that validates biological analysis-run metadata, produces
structured validation reports, and creates or enriches
[RO-Crate](https://www.researchobject.org/ro-crate/) packages.

This repository is at **Milestone 0**: a minimal working CLI, a typed manifest
model, and synthetic examples. RO-Crate generation and the full validation
engine are not yet implemented.

## Install

```
uv sync
```

## Usage

Print the version:

```
uv run bio-run-crate version
```

Validate a run manifest:

```
uv run bio-run-crate validate examples/run_manifest.yaml
```

A valid manifest reports success; an invalid one prints a validation error and
exits with a non-zero status.

## Development

```
uv run pytest                    # tests
uv run ruff check .              # lint
uv run ruff format --check .     # formatting
uv run mypy src                  # type checking
```
