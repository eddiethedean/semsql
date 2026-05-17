"""Final coverage gaps."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ontosql.fastapi.negotiate import negotiate_onto_response
from ontosql.mapping.registry import MapperRegistry
from ontosql.query.expr import AndExpr, FieldRef, compile_expr
from ontosql.registry import PrefixRegistry
from ontosql.semantic.model import get_onto_property_meta, onto_property, parse_iri_id
from tests.models import Person, PersonMap

pytest.importorskip("fastapi")


def test_compile_and_expr_branch() -> None:
    from ontosql.compile.select import compile_select_plan

    expr = AndExpr((Person.name == "A", Person.name == "B"))
    plan = compile_select_plan(PersonMap, where=expr)
    assert plan.select is not None


def test_field_ref_operators() -> None:
    col = PersonMap.column_maps["name"].column
    resolve = lambda ref: col  # noqa: E731
    compile_expr(FieldRef(Person, "name").in_(["a"]), resolve)
    compile_expr(FieldRef(Person, "name").is_null(), resolve)


def test_registry_custom_prefixes() -> None:
    reg = PrefixRegistry(prefixes={"ex": "http://example.org/"})
    assert reg.prefixes()["ex"] == "http://example.org/"


def test_registry_compact_no_match() -> None:
    reg = PrefixRegistry(prefixes={"short": "http://a/"})
    assert reg.compact("http://totally.other/x") == "http://totally.other/x"


def test_registry_eq_false() -> None:
    assert PrefixRegistry() != object()


def test_onto_meta_callable_extra() -> None:
    from pydantic import Field

    from ontosql import OntoModel

    def extra() -> dict:
        return {}

    class M(OntoModel):
        id: int
        x: str = Field(default="a", json_schema_extra=extra)

    assert get_onto_property_meta(M, "x") == {}


def test_parse_iri_no_template() -> None:
    from ontosql import OntoModel

    class NoTpl(OntoModel):
        id: int

    assert parse_iri_id("http://x", NoTpl) is None


def test_negotiate_no_accept_no_jsonld() -> None:
    request = MagicMock()
    request.headers.get.return_value = None
    resp = negotiate_onto_response(request, ["not", "json"])
    assert resp.media_type == "application/json"


def test_negotiate_chosen_loop_fallback() -> None:
    request = MagicMock()
    request.headers.get.return_value = "application/n-triples"
    resp = negotiate_onto_response(request, "<s> <p> <o> .")
    assert "n-triples" in resp.media_type


def test_registry_register_duplicate_entity() -> None:
    reg = MapperRegistry()
    reg.register(PersonMap)
    with pytest.raises(ValueError, match="already registered"):
        reg.register(PersonMap)


def test_map_column_infer_name() -> None:
    from ontosql.mapping.map import Map

    m = Map(PersonMap.column_maps["name"].column, field="custom")
    assert m.semantic_field == "custom"


def test_plan_label_for_branches() -> None:
    from ontosql.compile.select import compile_select_plan

    plan = compile_select_plan(PersonMap)
    with pytest.raises(KeyError):
        plan.label_for("missing", nested="employer")


def test_parse_accept_text_wildcard() -> None:
    from ontosql.fastapi.negotiate import _parse_accept

    assert _parse_accept("text/*") == "text/turtle"


def test_negotiate_line_96(monkeypatch: pytest.MonkeyPatch) -> None:
    from ontosql.fastapi import negotiate as neg

    request = MagicMock()
    request.headers.get.return_value = "text/turtle"
    monkeypatch.setattr(neg, "_parse_accept", lambda _a: "unknown/mime")
    resp = negotiate_onto_response(request, {"@id": "x"})
    assert resp.media_type == "application/ld+json"


def test_nested_map_no_primary() -> None:
    from ontosql.mapping.map import NestedMap

    nm = NestedMap("x", Person, PersonMap.column_maps["id"].column == 1, object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="no primary_table"):
        _ = nm.target_table


def test_column_field_name_raises() -> None:
    from ontosql.mapping.map import _column_field_name

    class Col:
        pass

    with pytest.raises(ValueError, match="Cannot infer"):
        _column_field_name(Col())  # type: ignore[arg-type]


def test_field_ref_all_comparisons() -> None:
    ref = FieldRef(Person, "name")
    col = PersonMap.column_maps["name"].column
    resolve = lambda r: col  # noqa: E731
    compile_expr(ref != "x", resolve)
    compile_expr(ref < "x", resolve)
    compile_expr(ref <= "x", resolve)
    compile_expr(ref > "x", resolve)
    compile_expr(ref >= "x", resolve)


def test_compile_empty_or() -> None:
    from ontosql.query.expr import CompileError, OrExpr

    with pytest.raises(CompileError, match="Empty OR"):
        compile_expr(OrExpr(()), lambda ref: PersonMap.column_maps["name"].column)


def test_compile_sqlalchemy_binary() -> None:
    from sqlalchemy import true

    from ontosql.compile.select import compile_select_plan

    plan = compile_select_plan(PersonMap, where=true())
    assert plan.select is not None


def test_and_or_merge() -> None:
    from ontosql.query.expr import AndExpr, OrExpr, compile_expr

    col = PersonMap.column_maps["name"].column
    resolve = lambda ref: col  # noqa: E731
    inner = AndExpr((Person.name == "A",))
    compile_expr(inner & (Person.name == "B"), resolve)
    inner_or = OrExpr((Person.name == "A",))
    merged = inner_or | (Person.name == "B")
    assert len(merged.parts) == 2
    compile_expr(merged, resolve)


def test_column_name_only() -> None:
    from ontosql.mapping.map import _column_field_name

    class Col:
        name = "onlyname"

    assert _column_field_name(Col()) == "onlyname"  # type: ignore[arg-type]


def test_meta_invalid_onto_value() -> None:
    from pydantic import Field

    from ontosql import OntoModel
    from ontosql.semantic.model import ONTO_META_KEY

    class M(OntoModel):
        id: int
        x: str = Field(default="a", json_schema_extra={ONTO_META_KEY: "bad"})

    assert get_onto_property_meta(M, "x") == {}


def test_negotiate_json_fallback() -> None:
    request = MagicMock()
    request.headers.get.return_value = None
    resp = negotiate_onto_response(request, {"count": 1})
    assert resp.media_type == "application/ld+json"


def test_parse_accept_app_wildcard_no_single() -> None:
    from ontosql.fastapi.negotiate import _matches_known_mime, _parse_accept

    assert _parse_accept("application/*") is None
    assert _matches_known_mime("text/html") is None


def test_registry_get_keyerror() -> None:
    reg = MapperRegistry()
    with pytest.raises(KeyError, match="No mapper registered"):
        reg.get(Person)


def test_registry_has() -> None:
    reg = MapperRegistry()
    assert reg.has(Person) is False
    reg.register(PersonMap)
    assert reg.has(Person) is True


def test_prefix_registry_compact_no_scheme() -> None:
    assert PrefixRegistry().compact("localterm") == "localterm"


def test_prefix_registry_not_implemented_eq() -> None:
    assert PrefixRegistry().__eq__(42) == NotImplemented


def test_prefix_registry_context_without_vocab() -> None:
    ctx = PrefixRegistry().context_dict()
    assert "@vocab" not in ctx


def test_or_expr_merge_direct() -> None:
    from ontosql.query.expr import OrExpr, _or_expr

    o1 = OrExpr((Person.name == "A",))
    o2 = _or_expr(o1, Person.name == "B")
    assert len(o2.parts) == 2
    o3 = _or_expr(Person.name == "A", Person.name == "B")
    assert len(o3.parts) == 2


def test_negotiate_json_response_non_dict() -> None:
    request = MagicMock()
    request.headers.get.return_value = None
    resp = negotiate_onto_response(request, ["not", "a", "dict"])
    assert resp.media_type == "application/json"


def test_negotiate_jsonld_instance_no_accept() -> None:
    request = MagicMock()
    request.headers.get.return_value = None

    class Exportable:
        def to_jsonld(self) -> dict:
            return {"@id": "http://ex/z"}

    resp = negotiate_onto_response(request, Exportable())
    assert resp.media_type == "application/ld+json"


def test_get_onto_meta_missing_field() -> None:
    assert get_onto_property_meta(Person, "not_a_field") == {}


def test_meta_not_dict() -> None:
    from pydantic import Field

    from ontosql import OntoModel

    class M(OntoModel):
        id: int
        x: str = Field(default="a", json_schema_extra="string")  # type: ignore[arg-type]

    assert get_onto_property_meta(M, "x") == {}


def test_iter_onto_fields() -> None:
    from ontosql.semantic.model import iter_onto_fields

    assert len(iter_onto_fields(Person)) >= 3


def test_parse_iri_bad_int() -> None:
    assert parse_iri_id("https://data.example.org/person/not-int", Person) is None


@pytest.mark.asyncio
async def test_async_get_none(async_engine) -> None:
    from ontosql.session.async_session import AsyncOntoSession

    async with AsyncOntoSession(async_engine, maps=[PersonMap]) as session:
        assert await session.get(Person, id=999) is None


def test_sync_create_tables(sync_engine) -> None:
    from ontosql.session.sync import OntoSession
    from tests.models import OrgRow, PersonRow

    with OntoSession(sync_engine, maps=[PersonMap]) as session:
        session.create_tables(PersonRow, OrgRow)


def test_registry_repr() -> None:
    assert "PrefixRegistry" in repr(PrefixRegistry())


def test_onto_property_optional_keys() -> None:
    from ontosql import OntoModel

    class M(OntoModel):
        id: int
        x: str = onto_property(
            "schema:x",
            datatype="xsd:string",
            iri="http://x",
            language="en",
            graph="g",
        )

    meta = get_onto_property_meta(M, "x")
    assert meta["datatype"] == "xsd:string"
