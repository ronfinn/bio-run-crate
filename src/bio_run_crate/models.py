"""Typed data models for biological analysis-run manifests.

These models describe the *shape* of a run manifest. They intentionally carry
no business rules beyond structural and type validation; higher-level findings
(warnings, informational notes, cross-field rules) belong to a later milestone's
validation engine.
"""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict, Field


class Pipeline(BaseModel):
    """The analysis pipeline that produced a run."""

    model_config = ConfigDict(extra="forbid")

    name: str
    version: str


class Author(BaseModel):
    """A person credited with a run."""

    model_config = ConfigDict(extra="forbid")

    name: str
    orcid: str | None = None


class RunManifest(BaseModel):
    """A single biological analysis-run described by a YAML manifest."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    run_id: str
    title: str
    description: str | None = None
    modality: str
    created: datetime.date
    pipeline: Pipeline
    authors: list[Author] = Field(default_factory=list)
