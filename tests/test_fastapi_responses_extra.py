"""FastAPI response serialization branches."""

from __future__ import annotations

from ontosql.fastapi.responses import _serialize_data

pytest = __import__("pytest")
pytest.importorskip("fastapi")


def test_serialize_jsonld_dict_only() -> None:
    body, mt = _serialize_data({"@id": "http://ex/x", "@type": "Thing"}, "json-ld")
    assert mt == "application/ld+json"
    assert "@id" in body


def test_serialize_jsonld_non_callable_to_jsonld() -> None:
    class Broken:
        to_jsonld = 1

    body, mt = _serialize_data({"@id": "http://ex/y"}, "json-ld")
    assert mt == "application/ld+json"


def test_serialize_jsonld_string_body() -> None:
    body, mt = _serialize_data('{"@id": "http://ex/z"}', "json-ld")
    assert mt == "application/ld+json"


def test_serialize_jsonld_callable_only() -> None:
    class WithJsonLd:
        def to_jsonld(self) -> dict:
            return {"@id": "http://ex/y"}

    body, mt = _serialize_data(WithJsonLd(), "json-ld")
    assert mt == "application/ld+json"
