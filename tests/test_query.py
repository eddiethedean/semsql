"""Tests for query expression compilation."""

from __future__ import annotations

import pytest
from sqlalchemy import column

from ontosql.query.expr import CompileError, compile_expr
from tests.models import Person


def test_compile_comparison() -> None:
    col = column("name")
    expr = Person.name == "Ada"
    clause = compile_expr(expr, lambda ref: col)
    assert clause is not None


def test_compile_startswith() -> None:
    col = column("name")
    expr = Person.name.startswith("A")
    clause = compile_expr(expr, lambda ref: col)
    assert "LIKE" in str(clause).upper() or "like" in str(clause)


def test_compile_and() -> None:
    col = column("name")
    expr = (Person.name.startswith("A")) & (Person.name == "Ada")
    clause = compile_expr(expr, lambda ref: col)
    assert clause is not None


def test_compile_bare_field_raises() -> None:
    with pytest.raises(CompileError):
        compile_expr(Person.name, lambda ref: column("x"))


def test_compile_unsupported() -> None:
    with pytest.raises(CompileError):
        compile_expr("not-an-expr", lambda ref: column("x"))
