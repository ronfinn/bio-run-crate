"""The modality-agnostic core rule set.

Every rule here applies to *any* run manifest, whatever produced it, and every
one is grounded in an explicit statement in ``docs/data-model.md`` Part A —
either an invariant the generic model needs to be internally coherent, or a
documented recommendation whose being unmet is worth reporting.

Deliberately **not** encoded here:

- anything Pydantic already enforces (required fields, types, non-empty strings,
  identifier patterns, unknown keys). Restating those as ``CORE-*`` rules would
  duplicate structural validation rather than add to it;
- anything Part A explicitly *permits*, such as an empty ``inputs`` or
  ``outputs`` list. Flagging a documented-valid state would be new product
  policy, not validation of the agreed model (see ``docs/data-model.md`` §A.9);
- heuristics that merely look like mistakes, such as two resource entries
  sharing a ``path``, which the model permits and which can be legitimate
  (one file described under two roles);
- anything requiring modality knowledge, an ontology lookup, the network, or the
  local filesystem (paths in a manifest are not resolved or opened here);
- anything requiring the current time, which would make output non-deterministic.

Rules take a parsed manifest and return findings; they never mutate it.

Rule numbering
--------------

``CORE-002``, ``CORE-004`` and ``CORE-005`` were drafted during development —
duplicate resource paths, empty ``outputs`` and empty ``inputs`` respectively —
and removed before ever being released, because each encoded a policy the data
model does not state (see ``docs/data-model.md`` §A.9). They were never assigned
in any released version, so they are *not* tombstoned in
:data:`RETIRED_CORE_RULE_IDS`, which is reserved for identifiers that were
genuinely published. They are simply left unallocated and are not reused here.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence

from bio_run_crate.findings import CORE_NAMESPACE, Finding, Location, Severity
from bio_run_crate.models import InputResource, OutputResource, RunManifest
from bio_run_crate.validation.registry import RuleRegistry
from bio_run_crate.validation.rule import Rule

DUPLICATE_RESOURCE_ID = "CORE-001"
OUTPUT_WITHOUT_CHECKSUM = "CORE-003"

#: Identifiers that were published and then retired, and so must never be
#: reused (``docs/data-model.md`` §A.8.1). Empty: no released core rule has been
#: retired. See "Rule numbering" above for identifiers dropped pre-release.
RETIRED_CORE_RULE_IDS: frozenset[str] = frozenset()


def _collections(
    manifest: RunManifest,
) -> tuple[tuple[str, Sequence[InputResource | OutputResource]], ...]:
    """Return the manifest's resource collections in a fixed order.

    Each entry pairs the collection's field name — used to build finding
    locations — with its resources.
    """
    return (("inputs", manifest.inputs), ("outputs", manifest.outputs))


def _check_duplicate_resource_ids(manifest: RunManifest) -> Iterator[Finding]:
    """CORE-001: a resource identifier identifies exactly one resource.

    ``docs/data-model.md`` §A.7 requires each resource to carry an identifier
    within its collection; one finding is emitted per repeat occurrence, so a
    value used three times is reported twice.
    """
    for field, resources in _collections(manifest):
        first_seen: dict[str, int] = {}
        for index, resource in enumerate(resources):
            first = first_seen.setdefault(resource.id, index)
            if first != index:
                yield Finding(
                    rule_id=DUPLICATE_RESOURCE_ID,
                    severity=Severity.ERROR,
                    message=(
                        f"Resource identifier {resource.id!r} is used more than "
                        f"once in {field} (first used at {field}[{first}]); "
                        f"identifiers must be unique within their collection."
                    ),
                    location=Location.from_parts(field, index, "id"),
                )


def _check_outputs_have_checksums(manifest: RunManifest) -> Iterator[Finding]:
    """CORE-003: a checksum is recommended for every output (§A.7)."""
    for index, output in enumerate(manifest.outputs):
        if output.checksum is None:
            yield Finding(
                rule_id=OUTPUT_WITHOUT_CHECKSUM,
                severity=Severity.WARNING,
                message=(
                    f"Output {output.id!r} has no checksum; a checksum is "
                    f"recommended for outputs so the artifact can be verified."
                ),
                location=Location.from_parts("outputs", index, "checksum"),
            )


CORE_RULES: tuple[Rule, ...] = (
    Rule(
        rule_id=DUPLICATE_RESOURCE_ID,
        severity=Severity.ERROR,
        description="Resource identifiers are unique within their collection.",
        check=_check_duplicate_resource_ids,
    ),
    Rule(
        rule_id=OUTPUT_WITHOUT_CHECKSUM,
        severity=Severity.WARNING,
        description="Every output carries a checksum.",
        check=_check_outputs_have_checksums,
    ),
)

#: The registry the engine uses by default. Constrained to the ``CORE``
#: namespace so a profile rule cannot be added to the core rule set by mistake.
CORE_REGISTRY = RuleRegistry(
    CORE_RULES,
    namespace=CORE_NAMESPACE,
    retired_rule_ids=RETIRED_CORE_RULE_IDS,
)
