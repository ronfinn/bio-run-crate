"""Registry of validation rules, and the invariants a rule set must satisfy.

``docs/data-model.md`` §A.8.1 states two rule-set-wide invariants that a single
finding cannot check: a rule number is **unique within its namespace**, and an
identifier is **never reused** once assigned.

Uniqueness is fully checkable at runtime and is enforced here, when a registry
is built. Non-reuse is a *historical* property: running code can only see the
rules that exist now, not the ones that once did. It is made checkable by
recording retired identifiers explicitly — a registry rejects any rule whose ID
appears in the retired ("tombstoned") set it was given. Retiring a *published*
rule therefore means deleting its :class:`~bio_run_crate.validation.rule.Rule`
*and* adding its ID to that set; nothing here can detect a retirement that was
never recorded, and this module does not claim to. An identifier that was only
ever drafted and dropped before release was never assigned to anything a user
could reference, so it does not need a tombstone.

A registry may also pin a namespace, so that the core rule set cannot silently
acquire a profile rule (or vice versa) — see ADR-0003.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping

from bio_run_crate.validation.rule import Rule


class RuleRegistry:
    """An immutable, ordered collection of rules with unique identifiers.

    Iterating a registry yields its rules in registration order. That order
    affects only the order checks happen to run in: the findings they produce
    are ordered canonically by
    :class:`~bio_run_crate.findings.ValidationResult`.
    """

    def __init__(
        self,
        rules: Iterable[Rule],
        *,
        namespace: str | None = None,
        retired_rule_ids: Iterable[str] = (),
    ) -> None:
        """Build a registry from ``rules``.

        Args:
            rules: The rules to register, in the order they should run.
            namespace: If given, every rule's identifier must use this
                namespace. The core registry pins ``CORE`` so that a profile
                rule cannot be added to the core rule set by mistake; a profile
                registry pins its own namespace the same way (ADR-0003).
            retired_rule_ids: Identifiers that were published and later retired,
                and so must never be reused.

        Raises:
            ValueError: if two rules share an identifier, if a rule's namespace
                does not match ``namespace``, or if a rule reuses a retired
                identifier.
        """
        retired = frozenset(retired_rule_ids)
        by_id: dict[str, Rule] = {}
        for rule in rules:
            if namespace is not None and rule.namespace != namespace:
                raise ValueError(
                    f"Rule {rule.rule_id} is not in the {namespace} namespace."
                )
            if rule.rule_id in by_id:
                raise ValueError(f"Duplicate rule identifier: {rule.rule_id}")
            if rule.rule_id in retired:
                raise ValueError(
                    f"Rule identifier {rule.rule_id} was retired and must not "
                    f"be reused."
                )
            by_id[rule.rule_id] = rule
        self._by_id = by_id
        self._namespace = namespace
        self._retired = retired

    def __iter__(self) -> Iterator[Rule]:
        return iter(self._by_id.values())

    def __len__(self) -> int:
        return len(self._by_id)

    def __contains__(self, rule_id: object) -> bool:
        return rule_id in self._by_id

    @property
    def rules(self) -> tuple[Rule, ...]:
        """The registered rules, in registration order."""
        return tuple(self._by_id.values())

    @property
    def namespace(self) -> str | None:
        """The namespace every rule must use, if the registry pins one."""
        return self._namespace

    @property
    def rule_ids(self) -> frozenset[str]:
        """The identifiers of the active rules."""
        return frozenset(self._by_id)

    @property
    def retired_rule_ids(self) -> frozenset[str]:
        """Identifiers this registry refuses to let a new rule reuse."""
        return self._retired

    def get(self, rule_id: str) -> Rule:
        """Return the rule with ``rule_id``.

        Raises:
            KeyError: if no such rule is registered.
        """
        return self._by_id[rule_id]

    def as_mapping(self) -> Mapping[str, Rule]:
        """Return a read-only view of the registry keyed by rule ID."""
        return dict(self._by_id)
