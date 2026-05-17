"""Tests for onto_model decorator."""

from __future__ import annotations

from sqlmodel import Field, SQLModel

from ontosql import OntoMixin, onto_field, onto_model


@onto_model(type_="schema:Thing", iri_template="http://example.org/thing/{id}")
class Thing(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)
    label: str = onto_field(ontology="rdfs:label")


def test_decorator_with_kwargs() -> None:
    t = Thing(id=7, label="Widget")
    doc = t.to_jsonld()
    assert doc["@type"] == "schema:Thing"
    assert doc["@id"] == "http://example.org/thing/7"


def test_bare_decorator() -> None:
    @onto_model
    class Bare(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)

    b = Bare(id=1)
    doc = b.to_jsonld()
    assert doc["@type"] == "Bare"
