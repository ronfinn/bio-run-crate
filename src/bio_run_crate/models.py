"""Typed data models for biological analysis-run manifests.

These models describe the *shape* of a run manifest: the project and dataset it
belongs to, its biological context (organism and optional tissue), the assay and
workflow that produced it, and its input and output resources.

They intentionally carry no business rules beyond structural, type and format
validation (required fields, value types, non-empty strings, synthetic-identifier
patterns). Higher-level findings — warnings, informational notes and cross-field
rules with stable identifiers and severities — belong to a later milestone's
validation engine, not here.
"""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# Synthetic-identifier patterns. Real sample/specimen identifiers must never
# appear in manifests (see docs/security-and-privacy.md); these patterns keep
# examples anchored to invented, public-safe values such as ``project-001``.
_RUN_ID = r"^run-\d{3,}$"
_PROJECT_ID = r"^project-\d{3,}$"
_DATASET_ID = r"^dataset-\d{3,}$"
_INPUT_ID = r"^input-\d{3,}$"
_OUTPUT_ID = r"^output-\d{3,}$"
_TAXON_ID = r"^NCBI:txid\d+$"
_UBERON_ID = r"^UBERON:\d{7}$"


class Project(BaseModel):
    """The project a run belongs to."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=_PROJECT_ID)
    title: str = Field(min_length=1)
    description: str | None = None
    url: HttpUrl | None = None


class Dataset(BaseModel):
    """The dataset a run produces or contributes to."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=_DATASET_ID)
    title: str = Field(min_length=1)
    description: str | None = None
    created: datetime.date | None = None


class Organism(BaseModel):
    """The source organism of the biological material."""

    model_config = ConfigDict(extra="forbid")

    scientific_name: str = Field(min_length=1)
    taxon_id: str | None = Field(default=None, pattern=_TAXON_ID)
    common_name: str | None = None


class Tissue(BaseModel):
    """The tissue or anatomical source of the biological material."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    ontology_id: str | None = Field(default=None, pattern=_UBERON_ID)


class BiologicalContext(BaseModel):
    """What the run's material is, biologically.

    ``tissue`` is optional: not every run has a tissue source (for example a
    cell line or a microbial culture).
    """

    model_config = ConfigDict(extra="forbid")

    organism: Organism
    tissue: Tissue | None = None


class Assay(BaseModel):
    """The measurement or assay that generated the data."""

    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=1)
    platform: str | None = None
    instrument_model: str | None = None


class Workflow(BaseModel):
    """The analysis workflow that produced the run."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    url: HttpUrl | None = None


class Resource(BaseModel):
    """A file or data artifact consumed or produced by a run.

    Shared base for :class:`InputResource` and :class:`OutputResource`; the two
    differ only in the pattern their ``id`` must match.
    """

    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1)
    role: str = Field(min_length=1)
    media_type: str | None = None
    checksum: str | None = None


class InputResource(Resource):
    """A resource consumed by a run."""

    id: str = Field(pattern=_INPUT_ID)


class OutputResource(Resource):
    """A resource produced by a run."""

    id: str = Field(pattern=_OUTPUT_ID)


class RunManifest(BaseModel):
    """A single biological analysis-run described by a YAML manifest."""

    model_config = ConfigDict(extra="forbid")

    manifest_version: str = Field(min_length=1)
    run_id: str = Field(pattern=_RUN_ID)
    project: Project
    dataset: Dataset
    biological_context: BiologicalContext
    assay: Assay
    workflow: Workflow
    inputs: list[InputResource]
    outputs: list[OutputResource]
