"""Structured validation findings.

Findings are the *output* of validating a manifest — the common currency
between the rule engine and the JSON/Markdown reporters. This module owns the
shape of that currency only: it defines what a finding is, how a rule is
identified, how a location inside a manifest is expressed, and how
findings are aggregated and ordered for one validation run.

It deliberately contains no validation rules. Concrete rules, the engine that
applies them, and the reporters that render these findings are separate
components (see ``docs/architecture.md`` §3.4 and §3.5).

Everything here is offline, deterministic and JSON-serialisable: models are
frozen, ``Severity`` serialises as its plain string name, and
:class:`ValidationResult` imposes a total order on its findings on every
construction path, so that two runs over the same manifest produce
byte-identical output.

Rule-ID convention
------------------

A rule identifier is ``<NAMESPACE>-<NNN>``:

- ``NAMESPACE`` is an uppercase namespace of letters and digits starting with a
  letter (2–16 characters). Core rules use ``CORE``; each validation profile
  uses its own distinct namespace (see ADR-0003).
- ``NNN`` is a zero-padded number of three or more digits.

Examples: ``CORE-001``, ``SEQ-014``. Rule IDs are part of this tool's public
surface: they may be referenced from audit records and suppression lists, so a
rule's severity or wording may change over time but its identifier must not.

:data:`RULE_ID_PATTERN` and :func:`is_valid_rule_id` check *syntax* only. That
each number is unique within its namespace and is never reused once assigned is
a project-level invariant over the whole rule set, which a single ``Finding``
cannot see; enforcing it is the job of the rule registry/engine (issue #6).
"""

from __future__ import annotations

import enum
import re
from collections.abc import Iterable
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator

#: Pattern every rule identifier must match. See the module docstring.
RULE_ID_PATTERN = r"^[A-Z][A-Z0-9]{1,15}-\d{3,}$"

#: Namespace reserved for the modality-agnostic core rule set.
CORE_NAMESPACE = "CORE"

#: Path used for a finding that applies to the manifest as a whole.
ROOT_PATH = "$"

_RULE_ID_RE = re.compile(RULE_ID_PATTERN)


class Severity(enum.StrEnum):
    """How serious a finding is.

    Exactly three severities exist. ``ERROR`` means the manifest is not
    acceptable; ``WARNING`` means it is acceptable but questionable; ``INFO``
    is an observation that requires no action.
    """

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


# Sort rank, most serious first. Kept separate from the enum members so that the
# serialised value stays a plain severity name rather than an integer.
_SEVERITY_RANK: dict[Severity, int] = {
    Severity.ERROR: 0,
    Severity.WARNING: 1,
    Severity.INFO: 2,
}


class Location(BaseModel):
    """Where in a manifest a finding applies.

    ``path`` is a textual pointer into the parsed manifest using dotted field
    names and bracketed list indices, for example ``inputs[0].checksum``. The
    manifest as a whole is :data:`ROOT_PATH`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: str = Field(min_length=1, default=ROOT_PATH)

    @classmethod
    def root(cls) -> Self:
        """Return the location referring to the whole manifest."""
        return cls(path=ROOT_PATH)

    @classmethod
    def from_parts(cls, *parts: str | int) -> Self:
        """Build a location from field names and list indices.

        ``Location.from_parts("inputs", 0, "checksum")`` yields the path
        ``inputs[0].checksum``. With no parts, the root location is returned.

        Raises:
            ValueError: if a string part is empty or an index is negative.
        """
        rendered = ""
        for part in parts:
            if isinstance(part, int):
                if part < 0:
                    raise ValueError(f"List index must not be negative: {part!r}")
                if not rendered:
                    raise ValueError("A location cannot start with a list index.")
                rendered += f"[{part}]"
            else:
                if not part:
                    raise ValueError("Location field names must not be empty.")
                rendered += part if not rendered else f".{part}"
        return cls(path=rendered or ROOT_PATH)

    def __str__(self) -> str:
        return self.path


class Finding(BaseModel):
    """A single validation observation about one manifest."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    rule_id: str = Field(pattern=RULE_ID_PATTERN)
    severity: Severity
    message: str = Field(min_length=1)
    location: Location = Field(default_factory=Location.root)

    @property
    def namespace(self) -> str:
        """The rule-ID namespace, e.g. ``CORE`` for ``CORE-001``."""
        return self.rule_id.split("-", 1)[0]

    def sort_key(self) -> tuple[int, str, str, str]:
        """Total-order key: severity, then location, rule ID and message."""
        return (
            _SEVERITY_RANK[self.severity],
            self.location.path,
            self.rule_id,
            self.message,
        )


class ValidationResult(BaseModel):
    """All findings produced by one validation run.

    ``findings`` is always held in canonical order regardless of how the result
    was built — direct construction, :meth:`model_validate`, JSON
    deserialisation or :meth:`from_findings`. Callers therefore cannot observe,
    or come to depend on, the order a rule engine happened to emit findings in.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    findings: tuple[Finding, ...] = ()

    @field_validator("findings", mode="after")
    @classmethod
    def _canonically_ordered(cls, findings: tuple[Finding, ...]) -> tuple[Finding, ...]:
        """Sort findings into canonical order on every construction path.

        Findings are ordered by severity (ERROR, then WARNING, then INFO), then
        by location path, rule ID and message. The key is total over everything
        that distinguishes one finding from another, so the input order can
        never affect the result. Sorting produces a new tuple; the caller's own
        collection is never mutated.
        """
        return tuple(sorted(findings, key=Finding.sort_key))

    @classmethod
    def from_findings(cls, findings: Iterable[Finding] = (), /) -> Self:
        """Return a result holding ``findings``, in canonical order.

        A convenience for building a result from any iterable. Ordering does not
        depend on using it — see :meth:`_canonically_ordered`.
        """
        return cls(findings=tuple(findings))

    def with_severity(self, severity: Severity) -> tuple[Finding, ...]:
        """Return only the findings of the given severity, order preserved."""
        return tuple(f for f in self.findings if f.severity is severity)

    def counts(self) -> dict[Severity, int]:
        """Return a count per severity, including severities with no findings."""
        counts = dict.fromkeys(Severity, 0)
        for finding in self.findings:
            counts[finding.severity] += 1
        return counts

    @property
    def has_errors(self) -> bool:
        """Whether any finding has ``ERROR`` severity."""
        return any(f.severity is Severity.ERROR for f in self.findings)


def is_valid_rule_id(rule_id: str) -> bool:
    """Whether ``rule_id`` follows the documented rule-ID convention."""
    return _RULE_ID_RE.match(rule_id) is not None
