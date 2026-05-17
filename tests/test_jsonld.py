"""Tests for JSON-LD serialization."""

from __future__ import annotations

import warnings

from sqlmodel import Field, SQLModel

from ontosql import OntoMixin, onto_field, onto_model
from tests.models import Employee, EmployeeFk, Organization, Person


def test_person_jsonld_structure(person: Person) -> None:
    doc = person.to_jsonld()
    assert "@context" in doc
    assert doc["@id"] == "http://example.org/person/1"
    assert doc["@type"] == "schema:Person"
    assert doc["schema:name"] == "Ada Lovelace"
    assert doc["schema:email"] == "ada@example.org"


def test_person_omits_none_fields(person: Person) -> None:
    p = Person(id=2, name="Bob")
    doc = p.to_jsonld()
    assert "schema:email" not in doc


def test_nested_organization(employee_with_org: Employee) -> None:
    doc = employee_with_org.to_jsonld()
    assert doc["schema:jobTitle"] == "Mathematician"
    org = doc.get("schema:worksFor")
    assert org is not None
    assert org["@type"] == "schema:Organization"
    assert org["schema:name"] == "Analytical Engines Inc."


def test_fk_reference_only() -> None:
    emp = EmployeeFk(id=3, title="Engineer", organization_id=99)
    doc = emp.to_jsonld()
    assert doc["schema:jobTitle"] == "Engineer"
    assert doc["schema:worksFor"] == {"@id": "http://example.org/org/99"}


def test_onto_context() -> None:
    ctx = Person.onto_context()
    assert "schema" in ctx


def test_duplicate_property_prefers_nested() -> None:
    """When FK and nested object share an ontology, nested wins."""

    @onto_model(type_="schema:Employee", iri_template="http://example.org/employee/{id}")
    class DualEmployee(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)
        organization_id: int | None = onto_field(
            default=None,
            ontology="schema:worksFor",
            related_model=Organization,
        )
        organization: Organization | None = onto_field(
            ontology="schema:worksFor",
            default=None,
        )

    org = Organization(id=2, name="Nested Org")
    emp = DualEmployee(id=1, organization_id=1, organization=org)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        doc = emp.to_jsonld()
    assert len(caught) == 1
    works_for = doc["schema:worksFor"]
    assert works_for["schema:name"] == "Nested Org"
    assert works_for["@id"] == "http://example.org/org/2"


def test_skips_fields_without_ontology_metadata(person: Person) -> None:
    """Fields without onto metadata are not exported."""

    @onto_model(type_="schema:Thing")
    class Thing(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)
        internal: str = "hidden"
        label: str = onto_field(ontology="rdfs:label")

    doc = Thing(id=1, label="visible").to_jsonld()
    assert "internal" not in doc
    assert doc["rdfs:label"] == "visible"
