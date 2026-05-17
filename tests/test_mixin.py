"""Integration tests for OntoMixin."""

from __future__ import annotations

from sqlmodel import Field, SQLModel

from ontosql import PrefixRegistry, apply_onto_model, onto_field
from ontosql.mixin import OntoMixin
from tests.models import Person


def test_to_jsonld_and_rdf(person: Person) -> None:
    j = person.to_jsonld()
    r = person.to_rdf()
    assert j["@id"]
    assert len(r) > 0


def test_custom_registry(person: Person) -> None:
    reg = PrefixRegistry().with_prefix("ex", "http://example.org/onto/")
    doc = person.to_jsonld(registry=reg)
    assert "@context" in doc


def test_apply_onto_model() -> None:
    class Item(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)
        label: str = onto_field(ontology="rdfs:label")

    apply_onto_model(Item, type_="ex:Item", iri_template="http://example.org/item/{id}")
    item = Item(id=5, label="Test")
    doc = item.to_jsonld()
    assert doc["@type"] == "ex:Item"
    assert doc["@id"] == "http://example.org/item/5"
