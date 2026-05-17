"""Semantic entity models (Pydantic)."""

from ontosql.semantic.model import (
    ONTO_META_KEY,
    OntoModel,
    build_instance_iri,
    get_onto_property_meta,
    iter_onto_fields,
    onto_property,
)

__all__ = [
    "ONTO_META_KEY",
    "OntoModel",
    "build_instance_iri",
    "get_onto_property_meta",
    "iter_onto_fields",
    "onto_property",
]
