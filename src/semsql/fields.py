"""Ontology-aware SQLModel field helper."""

from __future__ import annotations

from typing import Any

from sqlmodel import Field

from semsql._meta import ONTO_META_KEY


def onto_field(
    default: Any = ...,
    *,
    ontology: str | None = None,
    datatype: str | None = None,
    iri: str | None = None,
    inverse: str | None = None,
    language: str | None = None,
    graph: str | None = None,
    related_model: type[Any] | None = None,
    json_schema_extra: dict[str, Any] | None = None,
    schema_extra: dict[str, Any] | None = None,
    **kwargs: Any,
) -> Any:
    """
    Create a SQLModel Field with ontology metadata stored under ``semsql`` in
    ``json_schema_extra`` (via SQLModel's ``schema_extra``).
    """
    onto_meta: dict[str, Any] = {}
    if ontology is not None:
        onto_meta["ontology"] = ontology
    if datatype is not None:
        onto_meta["datatype"] = datatype
    if iri is not None:
        onto_meta["iri"] = iri
    if inverse is not None:
        onto_meta["inverse"] = inverse
    if language is not None:
        onto_meta["language"] = language
    if graph is not None:
        onto_meta["graph"] = graph
    if related_model is not None:
        onto_meta["related_model"] = related_model

    js_extra: dict[str, Any] = dict(json_schema_extra or {})
    existing_onto = js_extra.get(ONTO_META_KEY)
    if isinstance(existing_onto, dict):
        onto_meta = {**existing_onto, **onto_meta}
    js_extra[ONTO_META_KEY] = onto_meta

    merged_schema: dict[str, Any] = dict(schema_extra or {})
    existing_js = merged_schema.get("json_schema_extra")
    if isinstance(existing_js, dict):
        js_extra = {**existing_js, **js_extra}
    merged_schema["json_schema_extra"] = js_extra

    if default is ...:
        return Field(schema_extra=merged_schema, **kwargs)
    return Field(default, schema_extra=merged_schema, **kwargs)


def build_onto_extra(
    *,
    ontology: str | None = None,
    datatype: str | None = None,
    iri: str | None = None,
    inverse: str | None = None,
    language: str | None = None,
    graph: str | None = None,
) -> dict[str, Any]:
    """Build schema_extra dict for onto metadata (used in tests)."""
    onto_meta: dict[str, Any] = {}
    if ontology is not None:
        onto_meta["ontology"] = ontology
    if datatype is not None:
        onto_meta["datatype"] = datatype
    if iri is not None:
        onto_meta["iri"] = iri
    if inverse is not None:
        onto_meta["inverse"] = inverse
    if language is not None:
        onto_meta["language"] = language
    if graph is not None:
        onto_meta["graph"] = graph
    return {"json_schema_extra": {ONTO_META_KEY: onto_meta}}
