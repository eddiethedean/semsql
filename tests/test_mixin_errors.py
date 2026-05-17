"""OntoMixin edge cases."""

from __future__ import annotations

import pytest

from ontosql.mixin import OntoMixin


def test_onto_context_requires_sqlmodel() -> None:
    class Plain:
        pass

    with pytest.raises(TypeError):
        OntoMixin.onto_context(Plain)  # type: ignore[arg-type]
