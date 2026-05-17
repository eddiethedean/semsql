"""JSON-LD serialization for non-JSON-native Python types."""

from __future__ import annotations

import enum
import json
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import pytest
from sqlmodel import Field, SQLModel

from semsql import OntoMixin, onto_field, onto_model
from semsql.fastapi.responses import JSONLDResponse

pytest.importorskip("fastapi")


@onto_model(type_="ex:Event", iri_template="http://example.org/event/{id}")
class Event(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)
    when: datetime = onto_field(ontology="ex:when")
    day: date = onto_field(ontology="ex:day")


@onto_model(type_="ex:Account", iri_template="http://example.org/account/{id}")
class Account(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)
    uid: UUID = onto_field(ontology="ex:uid")
    balance: Decimal = onto_field(ontology="ex:balance")


class Status(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@onto_model(type_="ex:Record", iri_template="http://example.org/record/{id}")
class Record(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)
    status: Status = onto_field(ontology="ex:status")


@onto_model(type_="ex:Tagged", iri_template="http://example.org/tagged/{id}")
class Tagged(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)
    labels: tuple[str, ...] = onto_field(ontology="ex:labels")


def test_datetime_and_date_jsonld() -> None:
    inst = Event(id=1, when=datetime(2024, 1, 15, 12, 30), day=date(2024, 1, 15))
    doc = inst.to_jsonld()
    assert doc["ex:when"] == {
        "@value": "2024-01-15T12:30:00",
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
    }
    assert doc["ex:day"] == {
        "@value": "2024-01-15",
        "@type": "http://www.w3.org/2001/XMLSchema#date",
    }
    json.dumps(doc)


def test_uuid_and_decimal_jsonld() -> None:
    uid = UUID("12345678-1234-5678-1234-567812345678")
    inst = Account(id=1, uid=uid, balance=Decimal("99.50"))
    doc = inst.to_jsonld()
    assert doc["ex:uid"] == {
        "@value": str(uid),
        "@type": "http://www.w3.org/2001/XMLSchema#string",
    }
    assert doc["ex:balance"] == {
        "@value": "99.50",
        "@type": "http://www.w3.org/2001/XMLSchema#decimal",
    }
    json.dumps(doc)


def test_enum_jsonld() -> None:
    doc = Record(id=1, status=Status.ACTIVE).to_jsonld()
    assert doc["ex:status"] == "active"
    json.dumps(doc)


def test_tuple_serializes_as_list() -> None:
    doc = Tagged(id=1, labels=("a", "b")).to_jsonld()
    assert doc["ex:labels"] == ["a", "b"]
    json.dumps(doc)


def test_to_rdf_with_datetime() -> None:
    inst = Event(id=1, when=datetime(2024, 1, 15, 12, 30), day=date(2024, 1, 15))
    ttl = inst.to_rdf(format="turtle")
    assert len(ttl) > 0


def test_jsonld_response_with_datetime() -> None:
    inst = Event(id=1, when=datetime(2024, 1, 15, 12, 30), day=date(2024, 1, 15))
    resp = JSONLDResponse(inst)
    assert resp.media_type == "application/ld+json"
    parsed = json.loads(resp.body)
    assert parsed["ex:when"]["@value"] == "2024-01-15T12:30:00"
