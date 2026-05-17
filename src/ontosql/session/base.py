"""Shared session logic."""

from __future__ import annotations

from typing import Any

from ontosql.mapping.registry import MapperRegistry


class SessionBase:
    """Base for sync and async OntoSQL sessions."""

    def __init__(
        self,
        maps: list[type[Any]] | None = None,
        *,
        registry: MapperRegistry | None = None,
    ) -> None:
        self._registry = registry or MapperRegistry()
        if maps:
            self._registry.register_many(maps)

    def _mapper_for(self, entity_type: type[Any]) -> type[Any]:
        return self._registry.get(entity_type)
