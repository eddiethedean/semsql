# OntoModel Technical Specification

## Overview

**ontomodel** is a semantic interoperability framework built on SQLModel and Pydantic. It lets developers enrich SQLModel models with ontology-aware metadata and export or import data using semantic web standards — without leaving familiar Python model definitions.

| | |
|---|---|
| PyPI name | `ontomodel` |
| Import | `import ontomodel` |
| Python | 3.10+ |

## Core Components

1. `OntoMixin` — mixin for SQLModel classes
2. `onto_field()` — field helper with ontology metadata
3. `PrefixRegistry` — CURIE / namespace management
4. JSON-LD serializer
5. RDF graph adapter (RDFLib)
6. SHACL generator
7. FastAPI integration (`ontomodel.fastapi`)
8. Graph synchronization adapters

## Example API

```python
from sqlmodel import Field, SQLModel
from ontomodel import OntoMixin, onto_field


class Person(SQLModel, OntoMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str = onto_field(
        ontology="schema:name",
    )
```

Export:

```python
person = Person(id=1, name="Ada")
person.to_jsonld()
person.to_rdf(format="turtle")
```

## Ontology Field Metadata

`onto_field()` wraps SQLModel `Field()` and stores ontology metadata in `json_schema_extra`.

Supported keys:

| Key | Description |
|-----|-------------|
| `ontology` | Property IRI or CURIE (e.g. `schema:name`) |
| `datatype` | XSD or other datatype IRI |
| `iri` | Explicit property IRI override |
| `inverse` | Inverse property for relationships |
| `language` | Language tag for literals |
| `graph` | Named graph IRI |

## JSON-LD Support

- Automatic `@context` generation
- `@id` and `@type` handling
- Compact IRIs via `PrefixRegistry`
- Nested relationship serialization
- Optional framing (PyLD extra)

## RDF Support

RDFLib is used internally. Supported serializations:

- Turtle
- JSON-LD
- RDF/XML
- N-Triples

## SHACL Generation

OntoModel generates SHACL `NodeShape`s from SQLModel definitions.

| SQLModel / Python | SHACL |
|-------------------|-------|
| `str` | `sh:datatype xsd:string` |
| Optional field | `sh:minCount 0` |
| Required field | `sh:minCount 1` |
| Relationship | `sh:node` |

## FastAPI Integration

```python
from fastapi import FastAPI
from ontomodel.fastapi import OntoRouter

app = FastAPI()
app.include_router(OntoRouter(models=[Person]))
```

Features:

- Ontology-aware routers
- Content negotiation (`application/ld+json`, `text/turtle`, etc.)
- JSON-LD and RDF response classes
- OpenAPI enrichment with semantic metadata

## Persistence Model

Operational persistence stays relational via SQLModel and SQLAlchemy. Ontology export and import are an interoperability layer on top of the database — they do not replace it.

## Package Layout (proposed)

```text
ontomodel/
  __init__.py          # OntoMixin, onto_field, PrefixRegistry
  jsonld.py
  rdf.py
  shacl.py
  registry.py
  fastapi/
    __init__.py
    router.py
    responses.py
```

## Future Extensions

- SPARQL query layer
- Named graph support
- Ontology synchronization
- Graph database replication
- LLM extraction pipelines (`ontomodel[ai]`)
- Entity resolution

## Design Principles

- Pythonic APIs first
- Operational simplicity
- Standards compliance (JSON-LD, RDF, SHACL)
- Explicit over magical
- SQLModel compatibility
- Progressive enhancement via optional extras
