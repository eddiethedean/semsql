"""Tests for FastAPI integration."""

from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from semsql.fastapi import (
    JSONLDResponse,
    TurtleResponse,
    negotiate_onto_response,
)
from tests.models import Person

pytest.importorskip("fastapi")


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()

    @app.get("/person/{person_id}")
    def get_person(person_id: int, request: Request) -> object:
        person = Person(id=person_id, name="Ada Lovelace")
        return negotiate_onto_response(request, person)

    return TestClient(app)


def test_jsonld_default(client: TestClient) -> None:
    r = client.get("/person/1")
    assert r.status_code == 200
    assert "application/ld+json" in r.headers["content-type"]
    data = r.json()
    assert data["@id"] == "http://example.org/person/1"


def test_turtle_accept(client: TestClient) -> None:
    r = client.get("/person/1", headers={"Accept": "text/turtle"})
    assert r.status_code == 200
    assert "text/turtle" in r.headers["content-type"]
    assert "schema:name" in r.text or "schema.org" in r.text


def test_jsonld_response_direct(person: Person) -> None:
    resp = JSONLDResponse(person)
    assert resp.media_type == "application/ld+json"


def test_turtle_response_direct(person: Person) -> None:
    resp = TurtleResponse(person)
    assert resp.media_type == "text/turtle"
