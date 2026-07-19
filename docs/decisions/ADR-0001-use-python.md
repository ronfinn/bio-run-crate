# ADR-0001: Use Python 3.12 as the implementation language

## Status

Accepted (Milestone 0)

## Context

Bio Run Crate needs an implementation language and toolchain for a
command-line tool that parses YAML, validates structured data against
explicit rules, generates reports, and interoperates with an existing
Python library (`ro-crate-py`) for RO-Crate serialization. The tool is
aimed at contributors working in computational biology and research
data/software engineering, where Python is already a common shared
language, and needs to run without requiring users to install a heavy
runtime or build toolchain.

Relevant constraints from the project's working instructions
(`CLAUDE.md`):

- The RO-Crate creation step depends on `ro-crate-py`, which is a Python
  library. Using a different implementation language for the rest of the
  tool would mean either reimplementing RO-Crate serialization or bridging
  across a language boundary for that one step.
- The project favors small, typed functions and static type checking.
- Core validation must work fully offline with no network dependency.

## Decision

Use **Python 3.12**, with:

- **uv** for environment and dependency management (including a `src`
  package layout).
- **Typer** for the CLI.
- **Pydantic** for data models and validation.
- **PyYAML** for manifest parsing.
- **ro-crate-py** for RO-Crate 1.2 read/write (see ADR-0002).
- **pytest** for tests, **Ruff** for linting/formatting, **mypy** for
  static type checking.

This is a direct restatement of the "Technology" section of `CLAUDE.md`,
recorded here as a decision so the rationale is discoverable independent
of that file.

## Alternatives considered

This comparison is illustrative, reflecting the practical constraint that
`ro-crate-py` is a Python library, rather than a rigorous cross-language
benchmark. No formal evaluation (performance testing, team-skills survey,
etc.) was conducted.

| Option | Why not chosen |
|---|---|
| **Go or Rust** | Would offer a single static binary and strong performance, but there is no equivalent, actively used RO-Crate library in either ecosystem known to the authors at decision time; RO-Crate support would have to be built from scratch, which is out of scope for this project (RO-Crate serialization is meant to be an external dependency, not something this project owns). |
| **R** | Widely used in computational biology, but weaker fit for building a general-purpose CLI tool and packaging story compared to Python's CLI ecosystem (Typer) and typed-model ecosystem (Pydantic). |
| **JVM language (Java/Scala/Kotlin)** | Mature typing and tooling, but heavier runtime footprint for a CLI tool and no clear existing RO-Crate library advantage over Python's. |
| **Node.js/TypeScript** | Reasonable CLI ecosystem, but the RO-Crate JavaScript tooling landscape was not evaluated in depth, and Python was already effectively required by the `ro-crate-py` dependency. |

## Consequences

- The project inherits Python's packaging and distribution model
  (addressed later, see `docs/roadmap.md`).
- Static typing discipline (mypy) is a project-level choice, not something
  enforced by the language itself, so it depends on consistent contributor
  practice and CI enforcement.
- Choosing Python 3.12 specifically (rather than an older supported
  version) trades some environment-availability flexibility for newer
  language features; this has not been stress-tested against target
  deployment environments.

## Open questions / verification needed

- Whether Python 3.12 is available by default in all environments the
  project wants to support (for example, older Linux distributions, HPC
  cluster module systems commonly used in computational biology) has not
  been verified.
- No formal alternatives evaluation was performed; if a contributor
  believes another language/runtime would materially change the outcome,
  that should be raised as a new discussion rather than assumed settled by
  this ADR.
