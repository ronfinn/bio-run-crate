"""The rule abstraction shared by every validation rule.

A rule is a small, pure function over one already-parsed :class:`RunManifest`
that yields zero or more :class:`~bio_run_crate.findings.Finding` objects,
bundled with the metadata that makes it referenceable: a stable rule ID, the
severity it emits, and a short description of what it checks.

Rules never see the file, the raw YAML, or the CLI. They must be deterministic,
offline, and must not mutate the manifest they are given.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from bio_run_crate.findings import Finding, Severity, is_valid_rule_id
from bio_run_crate.models import RunManifest

#: The signature every rule check must have.
RuleCheck = Callable[[RunManifest], Iterable[Finding]]


@dataclass(frozen=True, slots=True)
class Rule:
    """One validation rule: its identity, its severity, and its check.

    Attributes:
        rule_id: Stable identifier following the ``<NAMESPACE>-<NNN>``
            convention (``docs/data-model.md`` §A.8.1).
        severity: The severity every finding this rule emits carries. One rule
            emits exactly one severity, by design: severity is then a property
            of the rule ID, so a reader of a report, an audit record or a
            suppression list can reason about ``CORE-001`` without also knowing
            which manifest produced it. A check that would want to report the
            same condition at two severities is two rules with two identifiers.
            :meth:`apply` enforces this contract rather than assuming it.
        description: One-line summary of the condition the rule checks.
        check: The check itself. It is called with a parsed manifest and must
            return an iterable of findings, deterministically and offline.
    """

    rule_id: str
    severity: Severity
    description: str
    check: RuleCheck

    @property
    def namespace(self) -> str:
        """The rule-ID namespace, e.g. ``CORE`` for ``CORE-001``.

        Nothing here is core-specific: a profile rule set uses this same class
        with its own namespace (ADR-0003), and a
        :class:`~bio_run_crate.validation.registry.RuleRegistry` can pin the
        namespace its rules must use.
        """
        return self.rule_id.split("-", 1)[0]

    def __post_init__(self) -> None:
        if not is_valid_rule_id(self.rule_id):
            raise ValueError(f"Invalid rule identifier: {self.rule_id!r}")
        if not self.description:
            raise ValueError(f"Rule {self.rule_id} must have a description.")

    def apply(self, manifest: RunManifest) -> tuple[Finding, ...]:
        """Run this rule against ``manifest`` and return its findings.

        The findings are returned in the order the check emitted them; callers
        must not depend on that order (see
        :class:`~bio_run_crate.findings.ValidationResult`).

        Raises:
            ValueError: if the check emits a finding attributed to a different
                rule, or at a severity the rule did not declare.
        """
        findings = tuple(self.check(manifest))
        for finding in findings:
            if finding.rule_id != self.rule_id:
                raise ValueError(
                    f"Rule {self.rule_id} emitted a finding attributed to "
                    f"{finding.rule_id}."
                )
            if finding.severity is not self.severity:
                raise ValueError(
                    f"Rule {self.rule_id} declares severity {self.severity} but "
                    f"emitted {finding.severity}."
                )
        return findings
