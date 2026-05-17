"""Metaclass for OntoModel query field access."""

from __future__ import annotations

from typing import Any, cast

from pydantic._internal._model_construction import ModelMetaclass


class OntoModelMeta(ModelMetaclass):
    """Pydantic metaclass that exposes semantic fields as query FieldRefs on the class."""

    def __getattr__(cls, name: str) -> Any:
        # Use __pydantic_fields__ directly — accessing model_fields recurses here.
        fields = cls.__dict__.get("__pydantic_fields__")
        if fields is not None and name in fields:
            from ontosql.query.expr import FieldRef

            return FieldRef(cast(Any, cls), name)
        raise AttributeError(f"{cls.__name__!r} has no attribute {name!r}")
