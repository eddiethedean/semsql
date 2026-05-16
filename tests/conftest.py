"""Pytest fixtures."""

from __future__ import annotations

import pytest

from tests.models import Employee, Organization, Person


@pytest.fixture
def person() -> Person:
    return Person(id=1, name="Ada Lovelace", email="ada@example.org")


@pytest.fixture
def organization() -> Organization:
    return Organization(id=10, name="Analytical Engines Inc.")


@pytest.fixture
def employee_with_org(organization: Organization) -> Employee:
    return Employee(id=2, title="Mathematician", organization=organization)
