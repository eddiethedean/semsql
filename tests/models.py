"""Shared SQLModel fixtures for tests."""

from __future__ import annotations

from sqlmodel import Field, SQLModel

from semsql import OntoMixin, onto_field, onto_model


@onto_model(type_="schema:Person", iri_template="http://example.org/person/{id}")
class Person(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)
    name: str = onto_field(ontology="schema:name")
    email: str | None = onto_field(ontology="schema:email", default=None)


@onto_model(type_="schema:Organization", iri_template="http://example.org/org/{id}")
class Organization(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)
    name: str = onto_field(ontology="schema:name")


@onto_model(type_="schema:Employee", iri_template="http://example.org/employee/{id}")
class Employee(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)
    title: str = onto_field(ontology="schema:jobTitle")
    organization_id: int | None = onto_field(
        default=None,
        foreign_key="organization.id",
        ontology="schema:worksFor",
        related_model=Organization,
    )
    organization: Organization | None = onto_field(ontology="schema:worksFor", default=None)
