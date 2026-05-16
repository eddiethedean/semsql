"""Tests for RDF serialization."""

from __future__ import annotations

import pytest

from ontomodel.rdf import media_type_for_format, normalize_format
from tests.models import Person


def test_normalize_format_aliases() -> None:
    assert normalize_format("turtle") == "turtle"
    assert normalize_format("ttl") == "turtle"
    assert normalize_format("json-ld") == "json-ld"
    assert normalize_format("n-triples") == "nt"


def test_unsupported_format() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        normalize_format("unsupported")


def test_person_turtle(person: Person) -> None:
    ttl = person.to_rdf(format="turtle")
    assert "schema:name" in ttl or "https://schema.org/name" in ttl


@pytest.mark.parametrize("fmt", ["turtle", "json-ld", "nt", "xml"])
def test_all_formats(person: Person, fmt: str) -> None:
    output = person.to_rdf(format=fmt)
    assert isinstance(output, str)
    assert len(output) > 0


def test_media_types() -> None:
    assert media_type_for_format("turtle") == "text/turtle"
    assert media_type_for_format("json-ld") == "application/ld+json"
