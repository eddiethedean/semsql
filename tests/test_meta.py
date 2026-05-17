"""Tests for internal _meta helpers."""

from __future__ import annotations

from pydantic import Field
from sqlmodel import SQLModel

from semsql import OntoMixin, apply_onto_model
from semsql._meta import (
    build_instance_iri,
    get_onto_meta,
    infer_xsd_datatype,
    literal_value_dict,
    property_key,
    reference_iri,
    resolve_curie,
)
from semsql.registry import PrefixRegistry


def test_get_onto_meta_empty() -> None:
    class M(SQLModel, table=False):
        x: str = Field()

    assert get_onto_meta(M.model_fields["x"]) == {}


def test_infer_xsd_and_literal() -> None:
    reg = PrefixRegistry()
    assert infer_xsd_datatype(int) == "xsd:integer"
    lit = literal_value_dict(42, {}, int, reg)
    assert lit == {"@value": 42, "@type": "http://www.w3.org/2001/XMLSchema#integer"}


def test_property_key_iri_override() -> None:
    reg = PrefixRegistry()
    key = property_key("n", {"iri": "http://example.org/custom"}, reg)
    assert key == "http://example.org/custom"


def test_build_instance_iri_template() -> None:
    class Item(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)
        slug: str = "x"

    apply_onto_model(Item, iri_template="http://example.org/items/{slug}/{id}")
    item = Item(id=1, slug="abc")
    iri = build_instance_iri(item, Item, PrefixRegistry())
    assert iri == "http://example.org/items/abc/1"


def test_reference_iri() -> None:
    class Ref(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)

    apply_onto_model(Ref, iri_template="http://example.org/ref/{id}")
    iri = reference_iri(Ref, 99, PrefixRegistry())
    assert iri == "http://example.org/ref/99"


def test_resolve_curie_absolute() -> None:
    reg = PrefixRegistry()
    assert resolve_curie("http://example.org/x", reg) == "http://example.org/x"


def test_registry_vocab_expand() -> None:
    reg = PrefixRegistry().with_vocab("http://example.org/vocab/")
    assert reg.expand("term") == "http://example.org/vocab/term"
