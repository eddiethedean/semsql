"""Tests for Accept header negotiation edge cases."""

from __future__ import annotations

from unittest.mock import MagicMock

from ontomodel.fastapi.negotiate import _parse_accept, negotiate_onto_response
from tests.models import Person


def test_parse_accept_empty() -> None:
    assert _parse_accept(None) is None
    assert _parse_accept("") is None


def test_parse_accept_turtle() -> None:
    assert _parse_accept("text/turtle, application/ld+json;q=0.8") == "text/turtle"


def test_negotiate_plain_dict() -> None:
    request = MagicMock()
    request.headers.get.return_value = None
    doc = {"@context": {}, "@id": "http://example.org/x"}
    resp = negotiate_onto_response(request, doc)
    assert resp.media_type == "application/ld+json"


def test_negotiate_ntriples() -> None:
    request = MagicMock()
    request.headers.get.return_value = "application/n-triples"
    person = Person(id=1, name="Ada")
    resp = negotiate_onto_response(request, person)
    assert resp.media_type == "application/n-triples"
