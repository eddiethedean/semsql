# OntoSQL Technical Specification

## Overview

**ontosql** is a semantic interoperability framework built on SQLModel and Pydantic. It lets developers enrich SQLModel models with ontology-aware metadata and export or import data using semantic web standards — without leaving familiar Python model definitions.

| | |
|---|---|
| PyPI name | `ontosql` |
| Import | `import ontosql` |
| Python | 3.10+ |

## Implementation status (0.1.0)

### Implemented

1. `OntoMixin` — mixin for SQLModel classes (`to_jsonld`, `to_rdf`, `onto_context`)
2. `onto_field()` / `@onto_model` — field and class ontology metadata
3. `PrefixRegistry` — CURIE expansion, compaction, JSON-LD `@context`
4. JSON-LD serializer — nested objects, FK references, typed literals (`datetime`, `UUID`, `Decimal`, `Enum`, tuples)
5. RDF export via RDFLib (Turtle, JSON-LD, N-Triples, RDF/XML)
6. FastAPI integration (`ontosql.fastapi`) — response classes and `negotiate_onto_response` content negotiation

### Planned (0.2+)

7. SHACL shape generation
8. RDF → SQLModel import
9. `OntoRouter` and OpenAPI semantic enrichment
10. Graph synchronization adapters
11. JSON-LD framing (PyLD extra)

## Example API

```python
from sqlmodel import Field, SQLModel
from ontosql import OntoMixin, onto_field


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
- Nested relationship serialization (prefer nested object over FK when both map to the same property)
- JSON-native coercion for `datetime`, `date`, `UUID`, `Decimal`, `Enum`, and `tuple` values
- Optional framing (PyLD extra, planned)

## RDF Support

RDFLib is used internally. Supported serializations:

- Turtle
- JSON-LD
- RDF/XML
- N-Triples

## SHACL Generation (planned)

SHACL `NodeShape` generation from SQLModel definitions is planned for 0.2+.

## FastAPI Integration (0.1.0)

```python
from fastapi import FastAPI, Request
from ontosql.fastapi import negotiate_onto_response

app = FastAPI()

@app.get("/person/{person_id}")
def get_person(person_id: int, request: Request):
  ...
  return negotiate_onto_response(request, person)
```

Implemented in 0.1.0:

- Content negotiation (`application/ld+json`, `text/turtle`, `application/n-triples`, `application/rdf+xml`)
- JSON-LD and RDF response classes (`JSONLDResponse`, `TurtleResponse`, etc.)
- `orjson` used for JSON-LD bodies when installed (`ontosql[fastapi]`)

Planned:

- `OntoRouter` for auto-generated CRUD routes
- OpenAPI enrichment with semantic metadata

## Persistence Model

Operational persistence stays relational via SQLModel and SQLAlchemy. Ontology export and import are an interoperability layer on top of the database — they do not replace it.

## Package Layout (0.1.0)

```text
src/ontosql/
  __init__.py          # OntoMixin, onto_field, PrefixRegistry
  _meta.py             # introspection and JSON-LD value coercion
  decorator.py         # onto_model
  fields.py            # onto_field
  mixin.py
  jsonld.py
  rdf.py
  registry.py
  fastapi/
    __init__.py
    negotiate.py
    responses.py
```

## Future Extensions

- SPARQL query layer
- Named graph support
- Ontology synchronization
- Graph database replication
- LLM extraction pipelines (`ontosql[ai]`)
- Entity resolution

## Design Principles

- Pythonic APIs first
- Operational simplicity
- Standards compliance (JSON-LD, RDF, SHACL)
- Explicit over magical
- SQLModel compatibility
- Progressive enhancement via optional extras
