"""Additional onto_field coverage."""

from __future__ import annotations

from sqlmodel import SQLModel

from ontomodel._meta import get_onto_meta
from ontomodel.fields import build_onto_extra, onto_field


class FullMeta(SQLModel, table=False):
    label: str = onto_field(
        "default",
        ontology="rdfs:label",
        datatype="xsd:string",
        iri="http://example.org/label",
        inverse="ex:inverse",
        language="en",
        graph="http://example.org/graph",
    )


def test_build_onto_extra_all_keys() -> None:
    extra = build_onto_extra(
        ontology="o",
        datatype="d",
        iri="i",
        inverse="inv",
        language="en",
        graph="g",
    )
    meta = extra["json_schema_extra"]["ontomodel"]
    assert meta["graph"] == "g"


def test_onto_field_schema_extra_merge() -> None:
    class M(SQLModel, table=False):
        x: str = onto_field(
            ontology="schema:name",
            schema_extra={"description": "label"},
        )

    info = M.model_fields["x"]
    assert info.description == "label"
    assert get_onto_meta(info)["ontology"] == "schema:name"


def test_all_onto_field_keys() -> None:
    meta = get_onto_meta(FullMeta.model_fields["label"])
    assert meta["ontology"] == "rdfs:label"
    assert meta["datatype"] == "xsd:string"
    assert meta["language"] == "en"
