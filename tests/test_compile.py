"""Tests for SELECT compilation."""

from __future__ import annotations

from ontosql.compile.select import compile_select_plan
from tests.models import Person, PersonMap


def test_compile_find_includes_join() -> None:
    plan = compile_select_plan(PersonMap, where=Person.name.startswith("A"))
    sql = str(plan.select.compile(compile_kwargs={"literal_binds": True}))
    assert "people" in sql.lower()
    assert "orgs" in sql.lower()
    assert "join" in sql.lower() or "LEFT OUTER JOIN" in sql.upper()


def test_compile_get_by_id() -> None:
    plan = compile_select_plan(PersonMap, id_value=1)
    sql = str(plan.select.compile(compile_kwargs={"literal_binds": True}))
    assert "1" in sql
