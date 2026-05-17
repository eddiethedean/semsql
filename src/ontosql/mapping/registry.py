"""Mapper registry."""

from __future__ import annotations

from typing import Any


class MapperRegistry:
    """Maps semantic entity types to OntoMapper classes."""

    def __init__(self) -> None:
        self._by_entity: dict[type[Any], type[Any]] = {}

    def register(self, mapper_cls: type[Any]) -> None:
        entity = mapper_cls.entity
        if entity in self._by_entity:
            existing = self._by_entity[entity]
            raise ValueError(
                f"Mapper already registered for {entity!r}: {existing!r} vs {mapper_cls!r}"
            )
        self._by_entity[entity] = mapper_cls

    def register_many(self, mapper_classes: list[type[Any]]) -> None:
        for mapper_cls in mapper_classes:
            self.register(mapper_cls)

    def get(self, entity_type: type[Any]) -> type[Any]:
        try:
            return self._by_entity[entity_type]
        except KeyError as exc:
            raise KeyError(f"No mapper registered for entity type {entity_type!r}") from exc

    def has(self, entity_type: type[Any]) -> bool:
        return entity_type in self._by_entity
