"""Semantic query expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import ColumnElement, and_, or_
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import ColumnElement as SAColumnElement

from ontosql.semantic.model import OntoModel


class CompileError(Exception):
    """Raised when a query expression cannot be compiled."""


@dataclass(frozen=True)
class FieldRef:
    """Reference to a semantic model field in a query."""

    model: type[OntoModel]
    field_name: str

    def __eq__(self, other: object) -> Comparison:  # ty: ignore[invalid-method-override]
        return Comparison(self, "eq", other)

    def __ne__(self, other: object) -> Comparison:  # ty: ignore[invalid-method-override]
        return Comparison(self, "ne", other)

    def __lt__(self, other: object) -> Comparison:
        return Comparison(self, "lt", other)

    def __le__(self, other: object) -> Comparison:
        return Comparison(self, "le", other)

    def __gt__(self, other: object) -> Comparison:
        return Comparison(self, "gt", other)

    def __ge__(self, other: object) -> Comparison:
        return Comparison(self, "ge", other)

    def in_(self, values: list[Any]) -> InList:
        return InList(self, values)

    def is_null(self) -> IsNull:
        return IsNull(self)

    def startswith(self, prefix: str) -> StartsWith:
        return StartsWith(self, prefix)


def _and_expr(left: Any, right: Any) -> AndExpr:
    if isinstance(left, AndExpr):
        return AndExpr((*left.parts, right))
    return AndExpr((left, right))


def _or_expr(left: Any, right: Any) -> OrExpr:
    if isinstance(left, OrExpr):
        return OrExpr((*left.parts, right))
    return OrExpr((left, right))


class _Combinable:
    def __and__(self, other: Any) -> AndExpr:
        return _and_expr(self, other)

    def __or__(self, other: Any) -> OrExpr:
        return _or_expr(self, other)


@dataclass(frozen=True)
class Comparison(_Combinable):
    left: FieldRef
    op: str
    right: Any


@dataclass(frozen=True)
class InList(_Combinable):
    left: FieldRef
    values: list[Any]


@dataclass(frozen=True)
class IsNull(_Combinable):
    left: FieldRef


@dataclass(frozen=True)
class StartsWith(_Combinable):
    left: FieldRef
    prefix: str


@dataclass(frozen=True)
class AndExpr(_Combinable):
    parts: tuple[Any, ...]


@dataclass(frozen=True)
class OrExpr(_Combinable):
    parts: tuple[Any, ...]


def compile_expr(expr: Any, column_for_field: Any) -> ColumnElement[bool]:
    """Compile a semantic expression to SQLAlchemy using field->column resolver."""
    if isinstance(expr, FieldRef):
        raise CompileError("Bare field reference is not a valid filter")

    if isinstance(expr, Comparison):
        col = column_for_field(expr.left)
        ops = {
            "eq": lambda c, v: c == v,
            "ne": lambda c, v: c != v,
            "lt": lambda c, v: c < v,
            "le": lambda c, v: c <= v,
            "gt": lambda c, v: c > v,
            "ge": lambda c, v: c >= v,
        }
        if expr.op not in ops:
            raise CompileError(f"Unknown comparison operator: {expr.op!r}")
        return ops[expr.op](col, expr.right)

    if isinstance(expr, InList):
        col = column_for_field(expr.left)
        return col.in_(expr.values)

    if isinstance(expr, IsNull):
        col = column_for_field(expr.left)
        return col.is_(None)

    if isinstance(expr, StartsWith):
        col = column_for_field(expr.left)
        return col.startswith(expr.prefix)  # type: ignore[attr-defined]

    if isinstance(expr, AndExpr):
        if not expr.parts:
            raise CompileError("Empty AND expression")
        return and_(*[compile_expr(p, column_for_field) for p in expr.parts])

    if isinstance(expr, OrExpr):
        if not expr.parts:
            raise CompileError("Empty OR expression")
        return or_(*[compile_expr(p, column_for_field) for p in expr.parts])

    if isinstance(expr, (BinaryExpression, SAColumnElement)):
        return expr  # type: ignore[return-value]

    raise CompileError(f"Unsupported filter expression: {type(expr)!r}")
