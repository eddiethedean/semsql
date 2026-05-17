# OntoSQL Architecture

> **Documentation describes 0.2.0 (in development).** [0.1.0 is deprecated](DEPRECATED-0.1.md) and unsupported.

## Problem

Real databases rarely match ontology shapes one-to-one:

- One semantic concept may span several tables (person + bridge + organization).
- One table may appear in multiple API or ontology views.
- Legacy columns exist that should never surface semantically.
- Ontology properties may be computed, joined, or read-only — not simple column mappings.

OntoSQL 0.2 treats **semantic models** as what application code uses, and **explicit maps** as how those models connect to SQL. Export and APIs are derived from the same definitions — not from assuming `table=True` classes are RDF entities.

## Glossary

| Term | Meaning |
|------|---------|
| **Semantic model** / **entity** | Pydantic `OntoModel` — what routes, services, and tests hold |
| **Physical model** / **row model** | SQLModel with `table=True` — mirrors actual tables |
| **Map** / **mapper** | `OntoMapper` — declarative binding from semantic fields to SQL |
| **Session** | `OntoSession` — unit of work; compiles CRUD to SQL |

## Layers

```mermaid
flowchart TB
    subgraph app [Application]
        Semantic["Person, Organization\nOntoModel"]
        Logic["get / find / save / delete"]
    end

    subgraph ontosql [OntoSQL]
        Mapper["PersonMap, OrganizationMap"]
        Compile["SQL compile + load"]
        Export["JSON-LD / RDF"]
    end

    subgraph db [Database]
        People["people"]
        Orgs["orgs"]
    end

    Semantic --> Logic
    Logic --> Mapper
    Mapper --> Compile
    Compile --> People
    Compile --> Orgs
    People --> Compile
    Compile --> Semantic
    Mapper --> Export
    Semantic --> Export
```

| Layer | Tool | Responsibility |
|-------|------|----------------|
| Physical | SQLModel (`table=True`) | Tables, FKs, indexes — DB truth |
| Semantic | Pydantic (`OntoModel`) | Application concepts, validation, ontology metadata |
| Mapping | `OntoMapper`, `Map` | Field → column/join; nested entities; cascade policies |
| Runtime | `OntoSession` | Transactions, identity, query compilation |
| Interop | `export` + `fastapi` | JSON-LD, RDF, content negotiation from mapper metadata |

### Why Pydantic + SQLModel (not one model)

- **SQLModel** fits schemas that already exist in Postgres — migrations stay familiar.
- **Pydantic** fits composed entities, nested graphs, and read vs write shapes without `table=True` awkwardness.
- Forcing a single class to be both row and entity caused the 0.1 design failure; 0.2 splits them on purpose.

## Mapping is explicit

Maps are **data you write and review**, not inference from table layout:

- Many tables → one semantic entity (joins, bridges).
- One table → many semantic maps (e.g. `schema:Person` vs `foaf:Person` views).
- Semantic-only fields (computed, constants) and physical-only columns (flags, versioning) are both supported.

See [SPECS.md](SPECS.md) for the mapper DSL and cascade policies.

## Read and write paths

**Read (`get`, `find`):**

1. Resolve `OntoMapper` for the semantic type.
2. Build a `SELECT` with required joins from field bindings.
3. Load flat rows into nested Pydantic instances.

**Write (`save`, `delete`) — planned 0.2.x / 0.3:**

1. Diff semantic instance against session state (partial updates via unset fields).
2. Plan `INSERT` / `UPDATE` / `DELETE` per physical table.
3. Apply nested **cascade policies** (`link`, `upsert`, `replace`, `ignore`) — never guessed.

```mermaid
sequenceDiagram
    participant App
    participant Session as OntoSession
    participant Mapper as OntoMapper
    participant DB as Database

    App->>Session: find(Person, where=...)
    Session->>Mapper: compile_select
    Mapper-->>Session: SQL + joins
    Session->>DB: execute
    DB-->>Session: rows
    Session->>Mapper: hydrate
    Mapper-->>App: list Person
```

## Interop

JSON-LD and RDF export walk **semantic instances + mapper metadata** (`type_iri`, `onto_property`, IRI templates). The same `PrefixRegistry` resolves CURIEs for queries and serialization.

Future milestones (see [ROADMAP.md](ROADMAP.md)): SHACL from maps, RDF import, graph sync — all mapper-driven, not column introspection.

## What changed from 0.1

0.1 attached ontology metadata to SQLModel fields and exported `instance.__dict__` as JSON-LD. That assumed one model ≈ one table.

0.2 removes that API entirely. There is no migration path — see [DEPRECATED-0.1.md](DEPRECATED-0.1.md).

## Non-goals

- Full OWL reasoning or Protégé-style ontology editing
- Arbitrary SPARQL-to-SQL as the primary query language
- Owning schema migrations (Alembic / user tooling stays in charge)
- Magical 1:1 inference from SQLAlchemy models to ontology classes

## Further reading

- [SPECS.md](SPECS.md) — target API contract
- [ROADMAP.md](ROADMAP.md) — release milestones
- [DEPS.md](DEPS.md) — dependency choices
