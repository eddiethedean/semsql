"""Pytest fixtures."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Session, SQLModel, create_engine

from ontosql import AsyncOntoSession, OntoSession
from tests.models import Organization, OrganizationMap, OrgRow, Person, PersonMap, PersonRow


@pytest.fixture
def sync_engine():
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(OrgRow(id=10, name="Analytical Engines Inc."))
        session.add(PersonRow(id=1, name="Ada Lovelace", org_id=10))
        session.add(PersonRow(id=2, name="Charles Babbage", org_id=10))
        session.add(PersonRow(id=3, name="Solo Person", org_id=None))
        session.commit()
    yield engine
    engine.dispose()


@pytest.fixture
def onto_session(sync_engine):
    with OntoSession(sync_engine, maps=[PersonMap, OrganizationMap]) as session:
        yield session


@pytest.fixture
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine) as session:
        session.add(OrgRow(id=10, name="Analytical Engines Inc."))
        session.add(PersonRow(id=1, name="Ada Lovelace", org_id=10))
        session.add(PersonRow(id=2, name="Charles Babbage", org_id=10))
        await session.commit()
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_onto_session(async_engine):
    async with AsyncOntoSession(async_engine, maps=[PersonMap, OrganizationMap]) as session:
        yield session


@pytest.fixture
def person() -> Person:
    return Person(
        id=1,
        name="Ada Lovelace",
        employer=Organization(id=10, name="Analytical Engines Inc."),
    )


@pytest.fixture
def organization() -> Organization:
    return Organization(id=10, name="Analytical Engines Inc.")
