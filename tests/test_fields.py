"""Tests for onto_field."""

from __future__ import annotations

from sqlmodel import Field, SQLModel

from semsql._meta import ONTO_META_KEY, get_onto_meta
from semsql.fields import build_onto_extra, onto_field


class Sample(SQLModel, table=False):
    name: str = onto_field(ontology="schema:name", datatype="xsd:string")
    bio: str | None = Field(
        default=None,
        schema_extra=build_onto_extra(ontology="schema:description"),
    )


def test_onto_field_stores_metadata() -> None:
    info = Sample.model_fields["name"]
    meta = get_onto_meta(info)
    assert meta["ontology"] == "schema:name"
    assert meta["datatype"] == "xsd:string"


def test_onto_field_merges_json_schema_extra() -> None:
    info = Sample.model_fields["bio"]
    meta = get_onto_meta(info)
    assert meta["ontology"] == "schema:description"
    extra = info.json_schema_extra
    assert isinstance(extra, dict)
    assert ONTO_META_KEY in extra


def test_model_instantiation() -> None:
    s = Sample(name="Ada", bio="Pioneer")
    assert s.name == "Ada"
