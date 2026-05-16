"""OntoMixin — semantic export methods for SQLModel classes."""

from __future__ import annotations

from typing import Any

from sqlmodel import SQLModel

from ontomodel.jsonld import class_context, model_to_jsonld
from ontomodel.rdf import model_to_rdf
from ontomodel.registry import PrefixRegistry


class OntoMixin:
    """
    Mixin providing JSON-LD and RDF export for SQLModel instances.

    Use with ``@onto_model`` and ``onto_field()`` for full semantic metadata.
    """

    def to_jsonld(self, *, registry: PrefixRegistry | None = None) -> dict[str, Any]:
        """Export this instance as a JSON-LD document."""
        return model_to_jsonld(self, registry=registry)  # type: ignore[arg-type]

    def to_rdf(
        self,
        *,
        format: str = "turtle",
        registry: PrefixRegistry | None = None,
    ) -> str:
        """Export this instance as an RDF string."""
        return model_to_rdf(self, format=format, registry=registry)  # type: ignore[arg-type]

    @classmethod
    def onto_context(cls, registry: PrefixRegistry | None = None) -> dict[str, Any]:
        """Return the JSON-LD @context for this model class."""
        if not issubclass(cls, SQLModel):
            raise TypeError("onto_context requires a SQLModel subclass")
        return class_context(cls, registry=registry)
