"""Internal metadata introspection for OntoSQL."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, get_args, get_origin
from uuid import UUID

from pydantic.fields import FieldInfo
from sqlmodel import SQLModel

from ontosql.registry import PrefixRegistry

ONTO_META_KEY = "ontosql"

# Fields to skip when serializing SQLModel / SQLAlchemy instances.
_SKIP_FIELDS = frozenset({"_sa_instance_state"})

# Python type -> XSD datatype CURIE (when field has no explicit datatype).
_PYTHON_XSD: dict[type[Any], str] = {
    str: "xsd:string",
    int: "xsd:integer",
    float: "xsd:double",
    bool: "xsd:boolean",
}


def get_onto_meta(field_info: FieldInfo) -> dict[str, Any]:
    """Extract ontology metadata from a Pydantic FieldInfo."""
    extra = field_info.json_schema_extra
    if extra is None:
        return {}
    if callable(extra):
        return {}
    if not isinstance(extra, dict):
        return {}
    meta = extra.get(ONTO_META_KEY)
    if isinstance(meta, dict):
        return dict(meta)
    return {}


def get_model_onto_type(model_cls: type[SQLModel]) -> str | None:
    """Return the RDF type CURIE/IRI for a model class, if set."""
    return getattr(model_cls, "__onto_type__", None)


def get_model_iri_template(model_cls: type[SQLModel]) -> str | None:
    """Return the IRI template for instances, if set."""
    return getattr(model_cls, "__onto_iri_template__", None)


def get_model_registry(model_cls: type[SQLModel]) -> PrefixRegistry | None:
    """Return a class-level PrefixRegistry override, if set."""
    return getattr(model_cls, "__onto_registry__", None)


def resolve_curie(curie: str, registry: PrefixRegistry) -> str:
    """Expand a CURIE to a full IRI, or return as-is if already absolute."""
    if "://" in curie or curie.startswith("urn:"):
        return curie
    return registry.expand(curie)


def property_key(field_name: str, meta: dict[str, Any], registry: PrefixRegistry) -> str:
    """Resolve the JSON-LD property key for a field."""
    if "iri" in meta:
        iri = str(meta["iri"])
        return registry.compact(iri) if "://" in iri else iri
    if "ontology" in meta:
        ont = str(meta["ontology"])
        return registry.compact(ont) if "://" in ont else ont
    return field_name


def infer_xsd_datatype(annotation: Any) -> str | None:
    """Infer XSD datatype CURIE from a Python type annotation."""
    origin = get_origin(annotation)
    if origin is not None:
        args = get_args(annotation)
        for arg in args:
            if arg is not type(None) and arg in _PYTHON_XSD:
                return _PYTHON_XSD[arg]
        return None
    if annotation in _PYTHON_XSD:
        return _PYTHON_XSD[annotation]
    return None


def is_onto_model_class(annotation: Any) -> bool:
    """Return True if annotation refers to a class using OntoMixin."""
    origin = get_origin(annotation)
    if origin is not None:
        args = get_args(annotation)
        return any(isinstance(arg, type) and _has_onto_mixin(arg) for arg in args)
    return isinstance(annotation, type) and _has_onto_mixin(annotation)


def get_nested_model_class(annotation: Any) -> type[Any] | None:
    """Return the nested OntoMixin model class from an annotation, if any."""
    origin = get_origin(annotation)
    candidates: list[Any] = []
    if origin is not None:
        candidates.extend(get_args(annotation))
    else:
        candidates.append(annotation)
    for candidate in candidates:
        if candidate is type(None):
            continue
        if isinstance(candidate, type) and _has_onto_mixin(candidate):
            return candidate
    return None


def _has_onto_mixin(cls: type[Any]) -> bool:
    from ontosql.mixin import OntoMixin

    return isinstance(cls, type) and issubclass(cls, OntoMixin)


def build_instance_iri(
    instance: SQLModel,
    model_cls: type[SQLModel],
    registry: PrefixRegistry,
) -> str:
    """Build @id for an instance."""
    template = get_model_iri_template(model_cls)
    if template:
        values = {name: getattr(instance, name, None) for name in model_cls.model_fields}
        try:
            return template.format(**values)
        except (KeyError, ValueError):
            pass
    pk = getattr(instance, "id", None)
    class_name = model_cls.__name__.lower()
    base = str(getattr(model_cls, "__onto_base_iri__", "http://example.org")).rstrip("/")
    if pk is not None:
        return f"{base}/{class_name}/{pk}"
    return f"{base}/{class_name}"


def iter_exportable_fields(model_cls: type[SQLModel]) -> list[tuple[str, FieldInfo]]:
    """Yield (name, FieldInfo) pairs that should appear in semantic export."""
    return [
        (name, info) for name, info in model_cls.model_fields.items() if name not in _SKIP_FIELDS
    ]


def coerce_jsonld_scalar(value: Any) -> Any:
    """Coerce a scalar Python value to a JSON-serializable form."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _auto_xsd_for_value(value: Any) -> str | None:
    """Infer XSD datatype CURIE from a runtime value."""
    if isinstance(value, datetime):
        return "xsd:dateTime"
    if isinstance(value, date):
        return "xsd:date"
    if isinstance(value, Decimal):
        return "xsd:decimal"
    if isinstance(value, UUID):
        return "xsd:string"
    return None


def literal_value_dict(
    value: Any,
    meta: dict[str, Any],
    annotation: Any,
    registry: PrefixRegistry,
) -> Any:
    """Wrap a literal value with @type / @language if metadata requires it."""
    coerced = coerce_jsonld_scalar(value)
    datatype = meta.get("datatype")
    language = meta.get("language")
    if datatype is None and language is None:
        inferred = infer_xsd_datatype(annotation)
        if inferred and isinstance(coerced, (int, float, bool)):
            return {"@value": coerced, "@type": resolve_curie(inferred, registry)}
        auto_xsd = _auto_xsd_for_value(value)
        if auto_xsd is not None:
            return {"@value": coerced, "@type": resolve_curie(auto_xsd, registry)}
        return coerced
    result: dict[str, Any] = {"@value": coerced}
    if datatype is not None:
        dt = str(datatype)
        result["@type"] = resolve_curie(dt, registry) if ":" in dt else dt
    if language is not None:
        result["@language"] = str(language)
    return result


def reference_iri(
    related_cls: type[SQLModel],
    fk_value: Any,
    registry: PrefixRegistry,
) -> str:
    """Build an @id reference for a foreign-key-only relationship."""
    template = get_model_iri_template(related_cls)
    if template:
        try:
            return template.format(id=fk_value)
        except (KeyError, ValueError):
            pass
    class_name = related_cls.__name__.lower()
    base = str(getattr(related_cls, "__onto_base_iri__", "http://example.org")).rstrip("/")
    return f"{base}/{class_name}/{fk_value}"


def is_list_annotation(annotation: Any) -> bool:
    """Return True if the annotation is a list, tuple, or other non-str Sequence."""
    origin = get_origin(annotation)
    if origin is list or origin is tuple:
        return True
    if origin is not None and origin is not str and isinstance(origin, type):
        try:
            if issubclass(origin, Sequence):
                return True
        except TypeError:
            pass
    return False


def is_fk_scalar(value: Any, nested_cls: type[Any] | None) -> bool:
    """Return True if value looks like a foreign-key id for nested_cls."""
    return nested_cls is not None and isinstance(value, int)
