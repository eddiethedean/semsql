"""Tests targeting 100% line and branch coverage."""

from __future__ import annotations

import builtins
import sys
from collections.abc import Sequence
from unittest.mock import MagicMock, patch

import pytest
from pydantic import Field
from pydantic.fields import FieldInfo
from sqlmodel import SQLModel

from ontosql import OntoMixin, apply_onto_model, onto_field, onto_model
from ontosql._meta import (
    build_instance_iri,
    coerce_jsonld_scalar,
    get_onto_meta,
    infer_xsd_datatype,
    is_fk_scalar,
    is_list_annotation,
    is_onto_model_class,
    literal_value_dict,
    property_key,
    reference_iri,
    resolve_curie,
)
from ontosql.decorator import _apply_onto_attrs
from ontosql.fastapi import negotiate as negotiate_mod
from ontosql.fastapi.negotiate import (
    _matches_known_mime,
    _parse_accept_params,
    negotiate_onto_response,
)
from ontosql.fastapi.responses import (
    JSONLDResponse,
    TurtleResponse,
    _dumps_json,
    _serialize_data,
)
from ontosql.jsonld import _serialize_single, model_to_jsonld
from ontosql.registry import PrefixRegistry
from tests.models import Organization, Person

pytest.importorskip("fastapi")


# --- _meta.py ---


def test_get_onto_meta_non_dict_extra() -> None:
    class M(SQLModel, table=False):
        x: str = Field(json_schema_extra=["not", "a", "dict"])  # type: ignore[arg-type]

    assert get_onto_meta(M.model_fields["x"]) == {}


def test_get_onto_meta_invalid_ontosql_value() -> None:
    class M(SQLModel, table=False):
        x: str = Field(json_schema_extra={"ontosql": "not-a-dict"})

    assert get_onto_meta(M.model_fields["x"]) == {}


def test_property_key_fallback_to_field_name() -> None:
    reg = PrefixRegistry()
    assert property_key("label", {}, reg) == "label"


def test_infer_xsd_optional_union() -> None:
    assert infer_xsd_datatype(int | None) == "xsd:integer"
    assert infer_xsd_datatype(str | int) == "xsd:string"


def test_infer_xsd_no_matching_arg() -> None:
    from datetime import datetime

    assert infer_xsd_datatype(datetime | None) is None


def test_property_key_absolute_ontology_iri() -> None:
    reg = PrefixRegistry()
    key = property_key("n", {"ontology": "https://schema.org/name"}, reg)
    assert key == "schema:name"


def test_build_instance_iri_without_pk() -> None:
    class NoPk(SQLModel, OntoMixin, table=False):
        name: str = onto_field(ontology="schema:name")

    apply_onto_model(NoPk, type_="schema:Thing")
    iri = build_instance_iri(NoPk(name="x"), NoPk, PrefixRegistry())
    assert iri == "http://example.org/nopk"


def test_build_instance_iri_template_format_error() -> None:
    class Bad(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)

    apply_onto_model(Bad, iri_template="http://example.org/bad/{missing}")
    iri = build_instance_iri(Bad(id=1), Bad, PrefixRegistry())
    assert iri == "http://example.org/bad/1"


def test_coerce_bytes() -> None:
    assert coerce_jsonld_scalar(b"hello") == "hello"


def test_coerce_unknown_returns_unchanged() -> None:
    class Custom:
        pass

    obj = Custom()
    assert coerce_jsonld_scalar(obj) is obj


def test_literal_datatype_without_colon() -> None:
    reg = PrefixRegistry()
    result = literal_value_dict("x", {"datatype": "plain"}, str, reg)
    assert result == {"@value": "x", "@type": "plain"}


def test_literal_language_only() -> None:
    reg = PrefixRegistry()
    result = literal_value_dict("bonjour", {"language": "fr"}, str, reg)
    assert result == {"@value": "bonjour", "@language": "fr"}


def test_reference_iri_without_template() -> None:
    class NoTpl(SQLModel, OntoMixin, table=False):
        pass

    apply_onto_model(NoTpl, type_="schema:Thing")
    assert reference_iri(NoTpl, 5, PrefixRegistry()) == "http://example.org/notpl/5"


def test_reference_iri_template_success() -> None:
    class Ref(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)

    apply_onto_model(Ref, iri_template="http://example.org/ref/{id}")
    assert reference_iri(Ref, 7, PrefixRegistry()) == "http://example.org/ref/7"


def test_reference_iri_template_fallback() -> None:
    class Ref(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)

    apply_onto_model(Ref, iri_template="http://example.org/ref/{missing}")
    iri = reference_iri(Ref, 7, PrefixRegistry())
    assert iri == "http://example.org/ref/7"


def test_is_list_annotation_abc_sequence() -> None:
    assert is_list_annotation(Sequence[str]) is True


def test_is_list_annotation_type_error_branch() -> None:
    assert is_list_annotation("not-a-type-annotation") is False

    with (
        patch("ontosql._meta.get_origin", return_value=type),
        patch("ontosql._meta.issubclass", side_effect=TypeError("bad")),
    ):
        assert is_list_annotation(Sequence[str]) is False


def test_resolve_curie_urn() -> None:
    reg = PrefixRegistry()
    urn = "urn:uuid:12345678-1234-5678-1234-567812345678"
    assert resolve_curie(urn, reg) == urn


def test_is_fk_scalar_false() -> None:
    assert is_fk_scalar("not-int", Organization) is False
    assert is_fk_scalar(1, None) is False


# --- decorator.py ---


def test_apply_onto_attrs_minimal() -> None:
    class Bare(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)

    _apply_onto_attrs(Bare, type_=None, iri_template=None, base_iri="http://base/", registry=None)
    assert Bare.__onto_base_iri__ == "http://base"
    assert not hasattr(Bare, "__onto_type__")


def test_apply_onto_attrs_type_only() -> None:
    class Typed(SQLModel, OntoMixin, table=False):
        pass

    _apply_onto_attrs(
        Typed,
        type_="schema:Thing",
        iri_template=None,
        base_iri="http://example.org",
        registry=None,
    )
    assert Typed.__onto_type__ == "schema:Thing"
    assert not hasattr(Typed, "__onto_iri_template__")


def test_apply_onto_attrs_iri_template_only() -> None:
    class Templated(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)

    _apply_onto_attrs(
        Templated,
        type_=None,
        iri_template="http://example.org/t/{id}",
        base_iri="http://example.org",
        registry=None,
    )
    assert Templated.__onto_iri_template__ == "http://example.org/t/{id}"
    assert not hasattr(Templated, "__onto_type__")


def test_apply_onto_attrs_with_registry() -> None:
    class WithReg(SQLModel, OntoMixin, table=False):
        pass

    reg = PrefixRegistry()
    _apply_onto_attrs(
        WithReg,
        type_=None,
        iri_template=None,
        base_iri="http://example.org",
        registry=reg,
    )
    assert WithReg.__onto_registry__ is reg


@onto_model(base_iri="http://custom.example")
class DecoratedBare(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)


@onto_model(
    type_="schema:Full",
    iri_template="http://example.org/full/{id}",
    base_iri="http://example.org",
    registry=PrefixRegistry(),
)
class FullyDecorated(SQLModel, OntoMixin, table=False):
    id: int | None = Field(default=None, primary_key=True)


def test_onto_model_bare_class_decorator() -> None:
    @onto_model
    class BareDecorated(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)

    assert BareDecorated.__onto_base_iri__ == "http://example.org"


def test_onto_model_parametrized_decorator() -> None:
    assert DecoratedBare.__onto_base_iri__ == "http://custom.example"
    assert FullyDecorated.__onto_type__ == "schema:Full"
    assert FullyDecorated.__onto_iri_template__ == "http://example.org/full/{id}"
    assert isinstance(FullyDecorated.__onto_registry__, PrefixRegistry)


# --- registry.py ---


def test_registry_init_with_prefixes() -> None:
    reg = PrefixRegistry(prefixes={"ex": "http://example.org/"})
    assert reg.expand("ex:Thing") == "http://example.org/Thing"


def test_registry_expand_no_colon_no_vocab() -> None:
    reg = PrefixRegistry()
    assert reg.expand("localterm") == "localterm"


def test_registry_repr() -> None:
    assert "PrefixRegistry" in repr(PrefixRegistry())


def test_registry_eq_not_implemented() -> None:
    assert PrefixRegistry().__eq__("other") is NotImplemented


def test_registry_compact_curie_without_slashes() -> None:
    reg = PrefixRegistry()
    assert reg.compact("schema:Person") == "schema:Person"


# --- fields.py ---


def test_onto_field_datatype_only() -> None:
    class M(SQLModel, table=False):
        n: int = onto_field(default=1, datatype="xsd:integer")

    meta = get_onto_meta(M.model_fields["n"])
    assert meta["datatype"] == "xsd:integer"
    assert "ontology" not in meta


def test_onto_field_merges_existing_ontosql_in_json_schema_extra() -> None:
    class M(SQLModel, table=False):
        x: str = onto_field(
            ontology="schema:name",
            json_schema_extra={"ontosql": {"inverse": "ex:inverse"}},
        )

    meta = get_onto_meta(M.model_fields["x"])
    assert meta["ontology"] == "schema:name"
    assert meta["inverse"] == "ex:inverse"


def test_onto_field_merges_schema_extra_json_schema_extra() -> None:
    class M(SQLModel, table=False):
        x: str = onto_field(
            ontology="schema:name",
            schema_extra={"json_schema_extra": {"description": "A name"}},
        )

    extra = M.model_fields["x"].json_schema_extra
    assert isinstance(extra, dict)
    assert extra.get("description") == "A name"


def test_build_onto_extra_datatype_only() -> None:
    from ontosql.fields import build_onto_extra

    extra = build_onto_extra(datatype="xsd:string")
    assert extra["json_schema_extra"]["ontosql"] == {"datatype": "xsd:string"}


def test_build_onto_extra_all_optional_keys() -> None:
    from ontosql.fields import build_onto_extra

    extra = build_onto_extra(
        ontology="o",
        datatype="xsd:string",
        iri="http://example.org/p",
        inverse="ex:inv",
        language="en",
        graph="http://example.org/g",
    )
    assert extra["json_schema_extra"]["ontosql"]["graph"] == "http://example.org/g"


def test_onto_field_all_optional_metadata_keys() -> None:
    class M(SQLModel, table=False):
        x: str = onto_field(
            default="v",
            iri="http://example.org/x",
            inverse="ex:inv",
            graph="http://example.org/g",
        )

    meta = get_onto_meta(M.model_fields["x"])
    assert meta["iri"] == "http://example.org/x"
    assert meta["inverse"] == "ex:inv"
    assert meta["graph"] == "http://example.org/g"


# --- jsonld.py ---


def test_model_to_jsonld_skips_none_serialized() -> None:
    person = Person(id=1, name="Ada")
    with patch("ontosql.jsonld._serialize_value", return_value=None):
        doc = model_to_jsonld(person)
    assert "schema:name" not in doc


def test_serialize_single_related_model_scalar_coercion() -> None:
    reg = PrefixRegistry()
    meta = {"related_model": Organization}
    result = _serialize_single("orphan", meta, str, reg, "x")
    assert result == "orphan"


def test_serialize_single_onto_class_int_fk() -> None:
    reg = PrefixRegistry()

    @onto_model(type_="schema:Org", iri_template="http://example.org/org/{id}")
    class Org(SQLModel, OntoMixin, table=False):
        id: int | None = Field(default=None, primary_key=True)

    result = _serialize_single(3, {}, Org | None, reg, "org_id")
    assert result == {"@id": "http://example.org/org/3"}


def test_serialize_single_onto_class_int_without_nested_cls() -> None:
    reg = PrefixRegistry()
    with (
        patch("ontosql.jsonld.get_nested_model_class", return_value=None),
        patch("ontosql.jsonld.is_onto_model_class", return_value=True),
    ):
        result = _serialize_single(3, {"ontology": "schema:id"}, Organization, reg, "org_id")
    assert result == 3


def test_serialize_single_onto_class_int_fk_via_is_onto_model_class() -> None:
    reg = PrefixRegistry()
    with (
        patch(
            "ontosql.jsonld.get_nested_model_class",
            side_effect=[None, Organization],
        ),
        patch("ontosql.jsonld.is_onto_model_class", return_value=True),
    ):
        result = _serialize_single(3, {}, Organization, reg, "org_id")
    assert result == {"@id": "http://example.org/org/3"}


def test_is_onto_model_class_direct() -> None:
    assert is_onto_model_class(Organization) is True


# --- fastapi negotiate ---


def test_parse_accept_params_empty_tokens() -> None:
    assert _parse_accept_params(";;;") == ("", 1.0)


def test_matches_known_mime_text_wildcard() -> None:
    assert _matches_known_mime("text/*") == "text/turtle"


def test_negotiate_defensive_jsonld_fallback() -> None:
    request = MagicMock()
    request.headers.get.return_value = "application/ld+json"
    person = Person(id=1, name="Ada")
    with patch.object(negotiate_mod, "_parse_accept", return_value="unknown/mime"):
        resp = negotiate_onto_response(request, person)
    assert resp.media_type == "application/ld+json"


# --- fastapi responses ---


def test_dumps_json_without_orjson(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "orjson":
            raise ImportError("no orjson")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    if "orjson" in sys.modules:
        monkeypatch.delitem(sys.modules, "orjson")
    body = _dumps_json({"a": 1})
    assert '"a": 1' in body


def test_serialize_data_jsonld_dict() -> None:
    body, media = _serialize_data({"@context": {}, "@id": "http://example.org/x"}, "json-ld")
    assert media == "application/ld+json"
    assert "@id" in body


def test_serialize_data_jsonld_prefers_to_jsonld_over_dict() -> None:
    person = Person(id=1, name="Ada")
    body, media = _serialize_data(person, "json-ld")
    assert media == "application/ld+json"
    assert "schema:name" in body


def test_serialize_data_jsonld_rejects_non_jsonld_data() -> None:
    with pytest.raises(TypeError, match="Response data must"):
        _serialize_data(object(), "json-ld")


def test_serialize_data_rdf_string() -> None:
    ttl = "@prefix ex: <http://example.org/> .\nex:s ex:p ex:o ."
    body, media = _serialize_data(ttl, "turtle")
    assert media == "text/turtle"
    assert body == ttl


def test_turtle_response_from_string() -> None:
    ttl = '@prefix schema: <https://schema.org/> .\n<> schema:name "Ada" .'
    resp = TurtleResponse(ttl)
    assert resp.media_type == "text/turtle"


def test_jsonld_response_uses_orjson_when_available() -> None:
    pytest.importorskip("orjson")
    person = Person(id=1, name="Ada")
    resp = JSONLDResponse(person)
    assert resp.media_type == "application/ld+json"
    assert b"@context" in resp.body


def test_field_export_priority_fk_branch() -> None:
    from ontosql.jsonld import _field_export_priority, _FieldExport

    entry = _FieldExport(
        field_name="organization_id",
        field_info=MagicMock(spec=FieldInfo),
        meta={"related_model": Organization},
        value=5,
        annotation=int,
    )
    assert _field_export_priority(entry) == 1
