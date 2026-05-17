"""IRI template fallback behavior."""

from __future__ import annotations

from sqlmodel import Field, SQLModel

from ontosql import OntoMixin, apply_onto_model, onto_field


def test_iri_template_fallback_on_missing_key() -> None:
    class Widget(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)
        name: str = onto_field(ontology="schema:name")

    apply_onto_model(Widget, type_="schema:Thing", iri_template="http://example.org/w/{missing}")
    doc = Widget(id=3, name="cog").to_jsonld()
    assert doc["@id"] == "http://example.org/widget/3"
