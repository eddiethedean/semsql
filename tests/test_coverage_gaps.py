"""Tests targeting remaining coverage gaps."""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi.responses import JSONResponse
from pydantic import Field
from sqlmodel import SQLModel

from ontosql import __version__, onto_field
from ontosql._meta import get_onto_meta
from ontosql.fastapi.negotiate import negotiate_onto_response
from ontosql.fastapi.responses import RDFXMLResponse
from tests.models import Person


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_get_onto_meta_callable_extra() -> None:
    def extra() -> dict[str, object]:
        return {}

    class M(SQLModel, table=False):
        x: str = Field(json_schema_extra=extra)

    assert get_onto_meta(M.model_fields["x"]) == {}


def test_onto_field_merges_json_schema_extra() -> None:
    class M(SQLModel, table=False):
        x: str = onto_field(
            ontology="schema:name",
            json_schema_extra={"other": True},
        )

    extra = M.model_fields["x"].json_schema_extra
    assert isinstance(extra, dict)
    assert extra.get("other") is True


def test_negotiate_rdf_xml() -> None:
    request = MagicMock()
    request.headers.get.return_value = "application/rdf+xml"
    person = Person(id=1, name="Ada")
    resp = negotiate_onto_response(request, person)
    assert isinstance(resp, RDFXMLResponse)


def test_negotiate_json_fallback() -> None:
    request = MagicMock()
    request.headers.get.return_value = "text/html"
    resp = negotiate_onto_response(request, "ok")
    assert isinstance(resp, JSONResponse)


def test_negotiate_q_value_parse_error() -> None:
    request = MagicMock()
    request.headers.get.return_value = "text/turtle;q=not-a-float"
    person = Person(id=1, name="Ada")
    resp = negotiate_onto_response(request, person)
    assert resp.media_type == "text/turtle"
