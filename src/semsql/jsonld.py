"""JSON-LD serialization for SemSQL instances."""

from __future__ import annotations

from typing import Any

from sqlmodel import SQLModel

from semsql._meta import (
    _has_onto_mixin,
    build_instance_iri,
    get_model_onto_type,
    get_model_registry,
    get_nested_model_class,
    get_onto_meta,
    is_list_annotation,
    is_onto_model_class,
    iter_exportable_fields,
    literal_value_dict,
    property_key,
    reference_iri,
)
from semsql.registry import PrefixRegistry


def default_registry() -> PrefixRegistry:
    return PrefixRegistry()


def model_to_jsonld(
    instance: SQLModel,
    *,
    registry: PrefixRegistry | None = None,
) -> dict[str, Any]:
    """Serialize a SQLModel instance with OntoMixin to a JSON-LD document."""
    model_cls = type(instance)
    reg = registry or get_model_registry(model_cls) or default_registry()

    doc: dict[str, Any] = {
        "@context": reg.context_dict(),
        "@id": build_instance_iri(instance, model_cls, reg),
    }

    onto_type = get_model_onto_type(model_cls)
    if onto_type:
        doc["@type"] = reg.compact(onto_type) if "://" in onto_type else onto_type
    else:
        doc["@type"] = model_cls.__name__

    for field_name, field_info in iter_exportable_fields(model_cls):
        meta = get_onto_meta(field_info)
        if not meta and field_name == "id":
            continue
        if not meta:
            continue

        value = getattr(instance, field_name, None)
        if value is None:
            continue

        key = property_key(field_name, meta, reg)
        annotation = field_info.annotation

        serialized = _serialize_value(
            value,
            meta,
            annotation,
            reg,
            field_name,
        )
        if serialized is not None:
            doc[key] = serialized

    return doc


def _serialize_value(
    value: Any,
    meta: dict[str, Any],
    annotation: Any,
    registry: PrefixRegistry,
    field_name: str,
) -> Any:
    if is_list_annotation(annotation):
        return [_serialize_single(item, meta, annotation, registry, field_name) for item in value]
    return _serialize_single(value, meta, annotation, registry, field_name)


def _serialize_single(
    value: Any,
    meta: dict[str, Any],
    annotation: Any,
    registry: PrefixRegistry,
    field_name: str,
) -> Any:
    nested_cls = get_nested_model_class(annotation)
    related = meta.get("related_model")
    if isinstance(related, type):
        nested_cls = related

    if nested_cls is not None:
        if _has_onto_mixin(type(value)) and hasattr(value, "to_jsonld"):
            nested_doc = model_to_jsonld(value, registry=registry)
            nested_doc.pop("@context", None)
            return nested_doc
        if isinstance(value, int):
            return {"@id": reference_iri(nested_cls, value, registry)}
        return value

    if is_onto_model_class(annotation) and isinstance(value, int):
        fk_cls = get_nested_model_class(annotation)
        if fk_cls is not None:
            return {"@id": reference_iri(fk_cls, value, registry)}

    return literal_value_dict(value, meta, annotation, registry)


def class_context(
    model_cls: type[SQLModel],
    registry: PrefixRegistry | None = None,
) -> dict[str, Any]:
    """Return JSON-LD @context for a model class."""
    reg = registry or get_model_registry(model_cls) or default_registry()
    return reg.context_dict()
