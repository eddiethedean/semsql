"""Advanced JSON-LD serialization cases."""

from __future__ import annotations

from sqlmodel import Field, SQLModel

from ontomodel import OntoMixin, onto_field, onto_model
from ontomodel.registry import PrefixRegistry
from tests.models import Employee, Person


@onto_model(type_="schema:Tag")
class Tag(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)
    labels: list[str] = onto_field(ontology="schema:keywords")


def test_list_field_serialization() -> None:
    tag = Tag(id=1, labels=["a", "b"])
    doc = tag.to_jsonld()
    assert doc["schema:keywords"] == ["a", "b"]


def test_fk_reference() -> None:
    emp = Employee(id=1, title="Dev", organization_id=5)
    doc = emp.to_jsonld()
    ref = doc.get("schema:worksFor")
    assert ref == {"@id": "http://example.org/org/5"}


def test_class_with_registry() -> None:
    reg = PrefixRegistry().with_prefix("ex", "http://example.org/")

    @onto_model(type_="ex:Item", registry=reg)
    class Item(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)
        name: str = onto_field(ontology="ex:name")

    doc = Item(id=1, name="X").to_jsonld()
    assert doc["@type"] == "ex:Item"


def test_literal_with_datatype_and_language(person: Person) -> None:
    reg = PrefixRegistry()

    @onto_model(type_="schema:Note")
    class Note(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)
        body: str = onto_field(ontology="schema:text", datatype="xsd:string", language="en")

    n = Note(id=1, body="hello")
    doc = n.to_jsonld(registry=reg)
    body = doc["schema:text"]
    assert body["@value"] == "hello"
    assert body["@language"] == "en"
