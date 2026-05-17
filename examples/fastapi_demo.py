"""Minimal FastAPI demo for OntoSQL content negotiation."""

from __future__ import annotations

from fastapi import FastAPI, Request
from sqlmodel import Field, SQLModel

from ontosql import OntoMixin, onto_field, onto_model
from ontosql.fastapi import negotiate_onto_response

app = FastAPI(title="OntoSQL Demo")


@onto_model(type_="schema:Person", iri_template="http://example.org/person/{id}")
class Person(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)
    name: str = onto_field(ontology="schema:name")


@app.get("/person/{person_id}")
def get_person(person_id: int, request: Request) -> object:
    person = Person(id=person_id, name="Ada Lovelace")
    return negotiate_onto_response(request, person)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
