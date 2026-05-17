"""Compiled select plan with column labels for hydration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.sql import Select


@dataclass
class ColumnProjection:
    """A selected column with a unique label."""

    label: str
    semantic_field: str
    column: Any
    source: str  # "root" or nested semantic field name


@dataclass
class SelectPlan:
    """Result of compiling a mapper to a SELECT."""

    select: Select[Any]
    projections: list[ColumnProjection] = field(default_factory=list)
    nested_projections: dict[str, list[ColumnProjection]] = field(default_factory=dict)
    mapper_cls: type[Any] | None = None

    def label_for(self, semantic_field: str, nested: str | None = None) -> str:
        if nested:
            for proj in self.nested_projections.get(nested, []):
                if proj.semantic_field == semantic_field:
                    return proj.label
        for proj in self.projections:
            if proj.semantic_field == semantic_field:
                return proj.label
        raise KeyError(f"No projection for field {semantic_field!r}")
