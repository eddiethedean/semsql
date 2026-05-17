# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-16

### Breaking

- Remove 0.1.0 export-on-table-model API: `OntoMixin`, `onto_field()`, `onto_model()`, `apply_onto_model()`, and export that introspects SQLModel table fields directly
- Remove 0.1 FastAPI integration that expects table-shaped `OntoMixin` instances as the primary response payload (semantic export wiring planned for 0.2.x)

### Added

- `OntoModel` and `onto_property` — Pydantic semantic entities with ontology metadata
- `OntoMapper`, `Map`, and `Map.nested` — declarative bindings from semantic fields to SQL columns and joins
- `OntoSession` (sync) and `AsyncOntoSession` — `get`, `find`, and `execute_sql` with semantic query expressions
- `PrefixRegistry` — retained for CURIE expansion and JSON-LD context (used by future export)
- Integration tests for Person / Organization nested `worksFor` over SQLite (sync and async)
- Example: `examples/person_org_demo.py`
- Documentation: [ARCHITECTURE.md](docs/ARCHITECTURE.md), [DEPRECATED-0.1.md](docs/DEPRECATED-0.1.md)

### Changed

- Project thesis: semantic data access over SQL via explicit maps (not annotate-and-export on table models)

### Not yet in 0.2.0

- `save` / `delete` and nested cascade policies (0.2.x / 0.3)
- `to_jsonld` / `to_rdf` on semantic instances (0.2.x)
- FastAPI negotiation wired to semantic export types (0.2.x)

## [0.1.0] - 2026-05-16

First public release of **OntoSQL** (`pip install ontosql`, `import ontosql`). **Deprecated in 0.2.0** — do not start new projects on 0.1.

### Added

- `onto_field()` — SQLModel field helper with ontology metadata in `json_schema_extra`
- `onto_model()` / `apply_onto_model()` — class decorator for RDF `@type` and instance IRI templates
- `OntoMixin` — `to_jsonld()`, `to_rdf()`, and `onto_context()` on model instances
- `PrefixRegistry` — CURIE expansion, compaction, and JSON-LD `@context` building
- JSON-LD export with `@context`, `@id`, `@type`, nested objects, and FK `@id` references
- RDF export via RDFLib (Turtle, JSON-LD, N-Triples, RDF/XML)
- JSON-safe literal coercion for `datetime`, `date`, `UUID`, `Decimal`, `Enum`, and `tuple`
- Optional `ontosql[fastapi]` extra: response classes and `negotiate_onto_response()` with `Accept` header negotiation
- Example FastAPI app in `examples/fastapi_demo.py`
- Documentation: `SPECS.md`, `PLAN.md`, `DEPS.md`, `ROADMAP.md`

### Fixed

- FastAPI `Accept` parsing now handles `charset`, `q` weights, and rejects `q=0` correctly
- Duplicate ontology property keys prefer nested objects over foreign-key integers (with warning)
- `orjson` used for JSON-LD responses when installed via the `fastapi` extra

[0.2.0]: https://github.com/eddiethedean/ontosql/releases/tag/v0.2.0
[0.1.0]: https://github.com/eddiethedean/ontosql/releases/tag/v0.1.0
