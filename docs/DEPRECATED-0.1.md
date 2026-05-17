# Deprecated: OntoSQL 0.1.0

**0.1.0 is removed in 0.2.0.** There is no compatibility shim and no migration guide.

## What 0.1 was

OntoSQL 0.1.0 was an **export-only** layer: annotate SQLModel classes with `onto_field()` and `@onto_model`, mix in `OntoMixin`, and call `to_jsonld()` / `to_rdf()` on instances. It assumed semantic entities aligned with table-shaped models.

## Removed public API

The following symbols are **not** part of 0.2:

| Symbol | Role in 0.1 |
|--------|----------------|
| `OntoMixin` | `to_jsonld()`, `to_rdf()`, `onto_context()` on table models |
| `onto_field()` | Ontology metadata on SQLModel `Field()` |
| `onto_model()` / `apply_onto_model()` | Class decorator for RDF type and IRI templates |
| Export-from-row | Serialization introspecting table model fields directly |

FastAPI helpers in 0.1 accepted the same table-shaped instances; 0.2 expects **semantic** instances produced by `OntoSession` (see [SPECS.md](SPECS.md)).

## If you must stay on 0.1

Install the last 0.1 release from PyPI or check out tag [`v0.1.0`](https://github.com/eddiethedean/ontosql/releases/tag/v0.1.0) on GitHub. That line receives no further updates.

## What to use instead

Read [ARCHITECTURE.md](ARCHITECTURE.md) and the [README](../README.md) quickstart for 0.2:

- **Physical models** — SQLModel `table=True`
- **Semantic models** — Pydantic `OntoModel`
- **Maps** — `OntoMapper` / `Map`
- **Runtime** — `OntoSession`

Historical 0.1 release notes remain in [CHANGELOG.md](../CHANGELOG.md#010---2026-05-16).
