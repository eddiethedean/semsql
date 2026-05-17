# OntoSQL Technical Specification

> **Target API (0.2.0).** This document describes the 0.2 contract. [0.1.0 is deprecated](DEPRECATED-0.1.md). Labels like *0.2.0-alpha* mark what ships in each milestone.

## Overview

| | |
|---|---|
| PyPI name | `ontosql` |
| Import | `import ontosql` |
| Python | 3.10+ |
| Thesis | Semantic CRUD over SQL via explicit maps |

**ontosql** is a semantic data access layer for Python: Pydantic semantic models, SQLModel physical tables, declarative `OntoMapper` bindings, and `OntoSession` that compiles operations to SQL. JSON-LD, RDF, and FastAPI responses are derived from the same mapping — not from annotating table rows.

See [ARCHITECTURE.md](ARCHITECTURE.md) for layers, glossary, and design rationale.

## Implementation phases

| Phase | Scope |
|-------|--------|
| **0.2.0-alpha** | Mapper registry, `get` / `find`, basic semantic filters, remove 0.1 public API |
| **0.2.x / 0.3** | `save` / `delete`, nested cascade policies, partial updates |
| **0.3** | `OntoRouter`, OpenAPI enrichment, bulk `find` |
| **0.4+** | SHACL from maps, RDF import, graph sync extras |

---

## Semantic models

### `OntoModel`

Base class for semantic entities (Pydantic v2).

```python
class Person(OntoModel):
    type_iri = "schema:Person"
    iri_template = "https://data.example.org/person/{id}"

    id: int
    name: str = onto_property("schema:name")
    employer: Organization | None = onto_property("schema:worksFor")
```

Class attributes:

| Attribute | Description |
|-----------|-------------|
| `type_iri` | RDF class CURIE or IRI (`@type`) |
| `iri_template` | Instance `@id` template; `{field}` placeholders from semantic fields |
| `registry` | Optional class-level `PrefixRegistry` override |

### `onto_property`

Field helper attaching ontology metadata to semantic fields.

| Key | Description |
|-----|-------------|
| `property` | Property CURIE or IRI (positional arg) |
| `datatype` | XSD or other datatype IRI |
| `iri` | Explicit property IRI override |
| `language` | Language tag for literals |
| `graph` | Named graph IRI (export) |

---

## Physical models

SQLModel classes with `table=True` mirror the database. They are **not** semantic entities.

```python
class PersonRow(SQLModel, table=True):
    __tablename__ = "people"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    org_id: int | None = Field(default=None, foreign_key="orgs.id")
```

- Migrations remain user-owned (Alembic, etc.).
- Unmapped columns are never touched by semantic CRUD unless bound in a map.

---

## Mapping

### `OntoMapper`

Declares how a semantic entity maps to SQL.

```python
class PersonMap(OntoMapper[Person]):
    entity = Person

    id = Map(PersonRow.id)
    name = Map(PersonRow.name, property="schema:name")
    employer = Map.nested(
        Organization,
        join=(PersonRow.org_id == OrgRow.id),
        target=OrgRow,
        nested_map=OrganizationMap,
        property="schema:worksFor",
    )
```

### `Map` bindings

| Binding | Use |
|---------|-----|
| `Map(column)` | Direct column |
| `Map(expr, property=...)` | SQLAlchemy column element |
| `Map.nested(...)` | Join + nested semantic type via another mapper |
| `Map.computed(...)` | Read-only semantic field from SQL expression *(planned)* |

### Cascade policies (write path — 0.2.x / 0.3)

Nested `save` behavior is **explicit** on `Map.nested`:

| Policy | Behavior |
|--------|----------|
| `link` | Update FK only; nested row must exist |
| `upsert` | Insert or update nested entity |
| `replace` | Replace nested association |
| `ignore` | Do not persist nested changes |

Default for new maps: `link` (fail closed on ambiguous graphs).

### Registry

- Register mappers with `OntoSession(maps=[...])` or a global registry helper *(API TBD)*.
- One physical table may have multiple mappers.
- One mapper per semantic entity type.

---

## Session

### `OntoSession`

Unit of work bound to a SQLAlchemy/SQLModel engine.

```python
async with OntoSession(engine, maps=[PersonMap, OrganizationMap]) as session:
    ...
```

| Method | Phase | Description |
|--------|-------|-------------|
| `get(entity, *, id=..., iri=...)` | 0.2.0-alpha | Load one instance by primary key or IRI |
| `find(entity, *, where=..., order_by=..., limit=..., offset=...)` | 0.2.0-alpha | Query with semantic field expressions |
| `save(instance)` | 0.2.x / 0.3 | Insert or update; returns hydrated instance |
| `delete(instance)` | 0.2.x / 0.3 | Delete per map delete plan |
| `execute_sql(...)` | 0.2.0-alpha | Escape hatch for raw SQL |

- Transactions: one transaction per `async with` block; explicit rollback on exception.
- Identity: optional identity map so repeated `get` in one session returns the same object *(planned)*.

### Query expressions

Filters reference **semantic** attributes; the session compiles joins from the mapper.

```python
await session.find(Person, where=Person.name.startswith("A"), limit=20)
```

Supported operators (target): comparisons, `startswith`, `in_`, `is_null`, boolean `&` / `|`. Unsupported expressions raise at compile time.

---

## `PrefixRegistry`

Retained from 0.1 (reimplemented against semantic/map metadata):

- CURIE `expand` / `compact`
- JSON-LD `@context` via `context_dict()`
- Copy-on-write `with_prefix`, `freeze()`

Used by session (IRI resolution), export, and FastAPI responses.

---

## Export

Export operates on **semantic instances** using mapper + `onto_property` metadata.

```python
person.to_jsonld(registry=None) -> dict
person.to_rdf(format="turtle", registry=None) -> str
```

| Format | Notes |
|--------|--------|
| JSON-LD | `@context`, `@id`, `@type`, nested objects |
| Turtle, N-Triples, RDF/XML | Via RDFLib |
| Literals | `datetime`, `date`, `UUID`, `Decimal`, `Enum`, `tuple` coercion |

RDFLib remains an implementation detail; users interact with Python models and strings.

---

## FastAPI (`ontosql[fastapi]`)

```python
from ontosql.fastapi import negotiate_onto_response

return negotiate_onto_response(request, semantic_instance)
```

| MIME type | Response |
|-----------|----------|
| `application/ld+json` | JSON-LD |
| `text/turtle` | Turtle |
| `application/n-triples` | N-Triples |
| `application/rdf+xml` | RDF/XML |

- RFC 7231-style `Accept` parsing (`q`, `charset`, `q=0` rejection).
- `orjson` for JSON-LD bodies when installed.

**0.3:** `OntoRouter` for CRUD routes; OpenAPI semantic enrichment.

---

## Target package layout

```text
src/ontosql/
  __init__.py
  semantic/       # OntoModel, onto_property
  physical/       # helpers for SQLModel registration (optional)
  mapping/        # OntoMapper, Map, registry
  compile/        # SQLAlchemy expression builders
  session/        # OntoSession, load strategies
  query/          # semantic expressions
  export/         # jsonld, rdf (from semantic + map)
  registry.py     # PrefixRegistry
  fastapi/
    negotiate.py
    responses.py
```

Current `main` may still reflect 0.1 layout until the rewrite merges.

---

## Anti-patterns

Do **not**:

- Use `table=True` on semantic `OntoModel` classes
- Assume one SQL table per ontology class
- Call `to_jsonld()` on SQLModel row instances without a session/map
- Map two semantic fields to the same property without a documented resolution rule
- Rely on automatic join inference without an explicit `Map.nested`

---

## Design principles

- Pythonic models first — semantic types are what you import in app code
- Explicit over magical — maps are reviewable data
- SQL is compiled, not hand-written for the happy path
- Standards compliance for **export** (JSON-LD, RDF); SHACL validation planned
- Progressive enhancement via optional extras (`fastapi`, future `shacl`, `jsonld`)

## Related documents

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [ROADMAP.md](ROADMAP.md)
- [DEPS.md](DEPS.md)
- [DEPRECATED-0.1.md](DEPRECATED-0.1.md)
