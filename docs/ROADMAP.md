# OntoSQL Roadmap

> **Documentation describes 0.2.0 (in development).** [0.1.0 is deprecated](DEPRECATED-0.1.md).

This document describes planned releases for **ontosql**. For the API contract, see [SPECS.md](SPECS.md). For dependency choices, see [DEPS.md](DEPS.md). For architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Vision

OntoSQL is the **operational semantic layer** for Python apps on SQL: define relational schemas with SQLModel, define application concepts with Pydantic semantic models, connect them with explicit maps, and get CRUD plus JSON-LD/RDF/FastAPI from one source of truth.

## Status on `main`

| Area | Status |
|------|--------|
| 0.1 export-on-table API | Removed in 0.2.0 |
| 0.2 mapper + session read | Implemented (`get`, `find`, sync + async) |
| 0.2 export / `save` / `delete` | Planned 0.2.x / 0.3 |
| PyPI | `0.2.0` pending release |

---

## v0.2.0 — Mapper and read path

**Theme:** Replace 0.1 with semantic data access; read before write.

### Planned

| Item | Notes |
|------|--------|
| `OntoModel`, `onto_property` | Semantic layer (Pydantic) |
| `OntoMapper`, `Map`, `Map.nested` | Explicit SQL bindings |
| `OntoSession.get` / `find` | Compiled SELECT + hydration |
| Semantic query expressions | Basic filters on mapped fields |
| `PrefixRegistry` | Retained; IRI + `@context` |
| Remove 0.1 API | `OntoMixin`, `onto_field`, `onto_model`, export-from-row |
| Documentation | ARCHITECTURE, SPECS, README for 0.2 |

### Success criteria

- Person / Organization example: multi-table schema, nested `worksFor`, `find` + `get` without hand-written JOINs
- No public 0.1 symbols in `ontosql` package root
- Tests cover mapper compile + load for representative joins

### Not in 0.2.0

- `save` / `delete` (see 0.2.x / 0.3)
- `OntoRouter`
- SHACL, RDF import

---

## v0.2.x / v0.3 — Write path and API ergonomics

**Theme:** Full CRUD and FastAPI integration.

### Planned

- **`save` / `delete`** — insert/update/delete plans across tables; transactions
- **Nested cascade policies** — `link`, `upsert`, `replace`, `ignore` on `Map.nested`
- **Partial updates** — `model_dump(exclude_unset=True)` drives PATCH-style SQL
- **Export** — `to_jsonld` / `to_rdf` from semantic instances + maps
- **`OntoRouter`** — auto-register CRUD routes
- **OpenAPI enrichment** — ontology IRIs and semantic media types in schema docs
- **Bulk `find`** — lists of semantic instances; pagination helpers
- **`ontosql[jsonld]` extra** — PyLD compaction and framing

### Success criteria

- Round-trip: create → read → update nested association → delete
- Demo app: CRUD + content negotiation in under ~30 lines of wiring

---

## v0.4 — Validation and graph interoperability

**Theme:** Close the loop between SQL and semantic graphs.

### Planned

- **SHACL generation** — `NodeShape`s from maps and semantic field types
- **RDF import** — hydrate semantic instances from JSON-LD / Turtle
- **Graph sync adapters** — push/pull to graph stores
- **SPARQL endpoint helpers** — read-only views of exported graphs
- **`ontosql[shacl]` extra** — optional pySHACL validation

### Success criteria

- Export → import preserves `@id`, `@type`, and mapped properties for representative models
- SHACL shapes validate graphs produced by session + export

---

## v1.0 — Stable platform

**Theme:** Production-ready public API and documentation site.

### Planned

- **API stability** — semver policy for `ontosql` and `ontosql.fastapi`
- **Schema packs** — curated prefix bundles (schema.org, Dublin Core, SKOS)
- **Production examples** — auth, pagination, multi-map apps
- **Documentation site** — MkDocs or equivalent; tutorials and migration from 0.1 history only

### Success criteria

- Documented upgrade path from 0.2.x → 1.0 (no 0.1 migration)
- Compatibility matrix: Python, SQLModel, Pydantic, FastAPI

---

## Long-term (post-1.0)

Strategic directions, not committed milestones:

| Direction | Description |
|-----------|-------------|
| **AI extraction** | Structured LLM output into `OntoModel` types (`ontosql[ai]`) |
| **OWL tooling** | Optional reasoning via Owlready2 |
| **Polars / ETL** | Ontology-aware DataFrame pipelines |
| **Entity resolution** | Link instances across datasets via shared IRIs |
| **LLM semantic memory** | Typed knowledge snippets for RAG backends |

---

## Explicit non-goals

OntoSQL will not replace:

- Full OWL reasoners or ontology IDEs (e.g. Protégé)
- Native graph query languages as the primary application API
- General-purpose ETL or data-lake orchestration
- Automatic 1:1 ORM inference from tables to ontology classes

Focus stays on **explicit maps** and **Pythonic semantic models**, with RDF as interoperability output.

---

## How milestones are chosen

1. **Mapper-first** — no feature that bypasses `OntoMapper` metadata
2. **Pydantic ergonomics** — app code uses semantic types, not row dumps
3. **Standards alignment** — JSON-LD 1.1, RDF 1.1 serializations, SHACL where applicable
4. **Optional weight** — heavy deps in extras (`fastapi`, `shacl`, `jsonld`, `graphdb`)
5. **Incremental delivery** — each minor version ships documented, testable scope

Feedback welcome via [GitHub Issues](https://github.com/eddiethedean/ontosql/issues).
