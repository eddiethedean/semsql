# OntoSQL Project Plan

## Vision

Build **ontosql** — a Python package that combines SQLModel, Pydantic, FastAPI, and ontology tooling into a unified semantic application framework. Developers define operational database models once and automatically gain semantic interoperability through JSON-LD, RDF, SHACL, and ontology-aware APIs.

```bash
pip install ontosql
```

## Core Thesis

Traditional ontology tooling is operationally difficult, while FastAPI + SQLModel ecosystems are highly ergonomic. OntoSQL bridges those worlds by adding ontology metadata and graph interoperability to normal Python web applications.

## Primary Goals

- Preserve SQLModel ergonomics
- Add ontology metadata to fields and models
- Enable JSON-LD and RDF export/import
- Generate SHACL shapes automatically
- Integrate deeply with FastAPI
- Support graph database synchronization
- Remain Pythonic and developer-friendly

## Target Users

- Enterprise data platform teams
- Knowledge graph engineers
- AI/RAG platform developers
- FastAPI backend teams
- Government and defense metadata systems
- Research and biomedical platforms

## MVP Scope

Version 0.1 should focus on:

- `OntoMixin`
- `onto_field()`
- JSON-LD export
- RDFLib graph export
- `PrefixRegistry`
- FastAPI content negotiation

## Non-Goals for v1

- Full OWL reasoning engine
- Native graph database query language
- Complex ontology editing UI
- Replacing RDF-native tooling like Protégé

## Suggested Stack

| Layer | Packages |
|-------|----------|
| Models | SQLModel, Pydantic v2 |
| API | FastAPI |
| Graph | RDFLib |
| Validation | pySHACL |
| HTTP | httpx |
| Typing | typing_extensions |

## Roadmap

### v0.1 (released)

- Ontology field metadata (`onto_field`, `@onto_model`)
- JSON-LD serialization (including typed literals and duplicate-property handling)
- RDF export (Turtle, JSON-LD, N-Triples, RDF/XML)
- `PrefixRegistry`
- FastAPI content negotiation and response classes (`ontosql[fastapi]`)

### v0.2

- SHACL generation
- RDF import
- Extended prefix / vocabulary management

### v0.3

- FastAPI `OntoRouter` and OpenAPI semantic enrichment

### v0.4

- Graph synchronization adapters
- SPARQL endpoint publishing

### v1.0

- Stable public API for `ontosql`
- Production examples
- Schema packs
- Full documentation

## Long-Term Vision

OntoSQL becomes the operational semantic layer for Python applications:

- Typed knowledge graphs
- AI semantic memory systems
- Metadata governance
- Enterprise interoperability
- LLM extraction pipelines
