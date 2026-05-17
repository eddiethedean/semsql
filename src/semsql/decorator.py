"""Class-level ontology metadata decorator."""

from __future__ import annotations

from typing import TypeVar, overload

from sqlmodel import SQLModel

from semsql.registry import PrefixRegistry

T = TypeVar("T", bound=type[SQLModel])


def _apply_onto_attrs(
    cls: type[SQLModel],
    *,
    type_: str | None,
    iri_template: str | None,
    base_iri: str,
    registry: PrefixRegistry | None,
) -> type[SQLModel]:
    if not issubclass(cls, SQLModel):
        raise TypeError(f"onto_model requires a SQLModel subclass, got {cls!r}")
    if type_ is not None:
        cls.__onto_type__ = type_
    if iri_template is not None:
        cls.__onto_iri_template__ = iri_template
    cls.__onto_base_iri__ = base_iri.rstrip("/")
    if registry is not None:
        cls.__onto_registry__ = registry
    return cls


@overload
def onto_model(cls: T, /) -> T: ...  # pragma: no cover


@overload
def onto_model(  # pragma: no cover
    cls: None = None,
    /,
    *,
    type_: str | None = ...,
    iri_template: str | None = ...,
    base_iri: str = ...,
    registry: PrefixRegistry | None = ...,
) -> object: ...


def onto_model(
    cls: type[SQLModel] | None = None,
    /,
    *,
    type_: str | None = None,
    iri_template: str | None = None,
    base_iri: str = "http://example.org",
    registry: PrefixRegistry | None = None,
) -> type[SQLModel] | object:
    """
    Class decorator attaching RDF type and IRI template metadata.

    Usage::

        @onto_model(type_="schema:Person", iri_template="http://example.org/person/{id}")
        class Person(SQLModel, OntoMixin, table=False):
            ...
    """

    def decorator(subcls: type[SQLModel]) -> type[SQLModel]:
        return _apply_onto_attrs(
            subcls,
            type_=type_,
            iri_template=iri_template,
            base_iri=base_iri,
            registry=registry,
        )

    if cls is not None:
        return decorator(cls)
    return decorator


def apply_onto_model(
    cls: type[SQLModel],
    *,
    type_: str | None = None,
    iri_template: str | None = None,
    base_iri: str = "http://example.org",
    registry: PrefixRegistry | None = None,
) -> type[SQLModel]:
    """Functional form of onto_model for use without decorator syntax."""
    return _apply_onto_attrs(
        cls,
        type_=type_,
        iri_template=iri_template,
        base_iri=base_iri,
        registry=registry,
    )
