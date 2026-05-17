"""Integration tests for AsyncOntoSession."""

from __future__ import annotations

import pytest

from tests.models import Person


@pytest.mark.asyncio
async def test_async_get(async_onto_session) -> None:
    person = await async_onto_session.get(Person, id=1)
    assert person is not None
    assert person.name == "Ada Lovelace"
    assert person.employer is not None


@pytest.mark.asyncio
async def test_async_find(async_onto_session) -> None:
    results = await async_onto_session.find(Person, where=Person.name.startswith("C"))
    assert len(results) == 1
    assert results[0].name == "Charles Babbage"
