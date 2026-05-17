"""OntoSQL — semantic data access for SQL."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from ontosql.mapping import Map, OntoMapper
from ontosql.registry import PrefixRegistry
from ontosql.semantic import OntoModel, onto_property
from ontosql.session import AsyncOntoSession, OntoSession

try:
    __version__ = version("ontosql")
except PackageNotFoundError:
    __version__ = "0.2.0"

__all__ = [
    "AsyncOntoSession",
    "Map",
    "OntoMapper",
    "OntoModel",
    "OntoSession",
    "PrefixRegistry",
    "__version__",
    "onto_property",
]
