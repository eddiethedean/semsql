"""OntoSQL session runtime."""

from ontosql.session.async_session import AsyncOntoSession
from ontosql.session.sync import OntoSession

__all__ = ["AsyncOntoSession", "OntoSession"]
