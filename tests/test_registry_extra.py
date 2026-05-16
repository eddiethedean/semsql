"""Additional PrefixRegistry tests."""

from __future__ import annotations

from ontomodel.registry import PrefixRegistry


def test_registry_eq_and_copy() -> None:
    a = PrefixRegistry()
    b = PrefixRegistry()
    assert a == b
    c = a.__copy__()
    assert c == a


def test_compact_unknown_iri() -> None:
    reg = PrefixRegistry()
    iri = "http://unknown.example.org/resource"
    assert reg.compact(iri) == iri


def test_with_vocab_frozen_error() -> None:
    reg = PrefixRegistry().freeze()
    try:
        reg.with_vocab("http://example.org/")
        raise AssertionError("expected RuntimeError")
    except RuntimeError:
        pass
