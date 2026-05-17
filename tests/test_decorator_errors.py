"""Decorator validation tests."""

from __future__ import annotations

import pytest

from ontosql import onto_model


def test_onto_model_requires_sqlmodel() -> None:
    class NotAModel:
        pass

    with pytest.raises(TypeError, match="SQLModel"):
        onto_model(NotAModel)
