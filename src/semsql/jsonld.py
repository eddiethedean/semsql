"""JSON-LD serialization for SemSQL instances."""

from __future__ import annotations

import warnings
from typing import Any

from pydantic.fields import FieldInfo
from sqlmodel import SQLModel

from semsql._meta import (
    _has_onto_mixin,
    build_instance_iri,
    coerce_jsonld_scalar,
    get_model_onto_type,
    get_model_registry,
    get_nested_model_class,
    get_onto_meta,
    is_fk_scalar,
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

    pending: dict[str, list[_FieldExport]] = {}
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
        pending.setdefault(key, []).append(
            _FieldExport(
                field_name=field_name,
                field_info=field_info,
                meta=meta,
                value=value,
                annotation=field_info.annotation,
            )
        )

    for key, entries in pending.items():
        if len(entries) > 1:
            warnings.warn(
                f"Multiple fields map to JSON-LD property {key!r} on {model_cls.__name__}; "
                "preferring nested object over foreign-key reference",
                stacklevel=2,
            )
        chosen = _choose_field_export(entries)
        serialized = _serialize_value(
            chosen.value,
            chosen.meta,
            chosen.annotation,
            reg,
            chosen.field_name,
        )
        if serialized is not None:
            doc[key] = serialized

    return doc


class _FieldExport:
    __slots__ = ("field_name", "field_info", "meta", "value", "annotation")

    def __init__(
        self,
        *,
        field_name: str,
        field_info: FieldInfo,
        meta: dict[str, Any],
        value: Any,
        annotation: Any,
    ) -> None:
        self.field_name = field_name
        self.field_info = field_info
        self.meta = meta
        self.value = value
        self.annotation = annotation


def _field_export_priority(entry: _FieldExport) -> int:
    """Higher score wins when multiple fields share the same property key."""
    nested_cls = get_nested_model_class(entry.annotation)
    related = entry.meta.get("related_model")
    if isinstance(related, type):
        nested_cls = related

    if (
        nested_cls is not None
        and _has_onto_mixin(type(entry.value))
        and hasattr(entry.value, "to_jsonld")
    ):
        return 3
    if is_fk_scalar(entry.value, nested_cls):
        return 1
    return 2


def _choose_field_export(entries: list[_FieldExport]) -> _FieldExport:
    return max(entries, key=_field_export_priority)


def _serialize_value(
    value: Any,
    meta: dict[str, Any],
    annotation: Any,
    registry: PrefixRegistry,
    field_name: str,
) -> Any:
    if is_list_annotation(annotation):
        items = list(value) if isinstance(value, tuple) else value
        return [_serialize_single(item, meta, annotation, registry, field_name) for item in items]
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
        return coerce_jsonld_scalar(value)

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
