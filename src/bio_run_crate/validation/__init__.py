"""Rule-based validation of parsed run manifests.

The public entry point is :func:`validate_manifest`, which applies the
modality-agnostic core rule set (:data:`CORE_REGISTRY`) to an already-parsed
:class:`~bio_run_crate.models.RunManifest` and returns a
:class:`~bio_run_crate.findings.ValidationResult`.

The package is layered: :mod:`~bio_run_crate.validation.rule` defines what a
rule is, :mod:`~bio_run_crate.validation.registry` holds a rule set and enforces
its identifier invariants, :mod:`~bio_run_crate.validation.core_rules` is the
core rule set itself, and :mod:`~bio_run_crate.validation.engine` applies one to
a manifest. Nothing here reads files, renders output, or chooses exit codes.
"""

from __future__ import annotations

from bio_run_crate.validation.core_rules import (
    CORE_REGISTRY,
    CORE_RULES,
    RETIRED_CORE_RULE_IDS,
)
from bio_run_crate.validation.engine import validate_manifest
from bio_run_crate.validation.registry import RuleRegistry
from bio_run_crate.validation.rule import Rule, RuleCheck

__all__ = [
    "CORE_REGISTRY",
    "CORE_RULES",
    "RETIRED_CORE_RULE_IDS",
    "Rule",
    "RuleCheck",
    "RuleRegistry",
    "validate_manifest",
]
