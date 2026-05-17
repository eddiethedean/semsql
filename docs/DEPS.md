# SemSQL Dependency Ecosystem Assessment

## Overview

This document evaluates recommended Python package dependencies and ecosystem integrations for **semsql**. The goal is to maintain a lightweight, Pythonic, operationally focused semantic interoperability framework centered on SQLModel and FastAPI.

## Dependency Philosophy

The `semsql` package should maintain:

- A small and stable core
- Optional extras for advanced integrations
- Strong SQLModel compatibility
- Minimal developer friction
- Pythonic APIs over RDF-native complexity

The package should avoid becoming a heavyweight semantic-web framework.

## Core Dependencies

### SQLModel

- Primary operational model layer
- SQLAlchemy + Pydantic integration
- FastAPI-native ergonomics

### Pydantic

- Validation and serialization
- Type system foundation
- JSON schema generation

### typing-extensions

- Advanced typing compatibility

### RDFLib

- RDF graph backend
- Serialization and parsing
- Namespace handling

## FastAPI Ecosystem Extras

### FastAPI

- Ontology-aware API integration
- Content negotiation
- OpenAPI enhancement

### orjson

- High-performance JSON serialization
- Efficient JSON-LD support

## Semantic Validation Extras

### pySHACL

- SHACL validation support
- RDF graph validation
- Enterprise interoperability validation

## JSON-LD Ecosystem

### PyLD

- JSON-LD compaction
- Framing
- Expansion
- Canonicalization

PyLD significantly improves JSON-LD capabilities beyond basic RDFLib support.

## Graph Database Integrations

### SPARQLWrapper

- SPARQL endpoint communication
- RDF graph database interoperability

### Neo4j Python Driver

- Property graph integrations
- Hybrid knowledge graph architectures

## AI and LLM Ecosystem

### Instructor

- Structured LLM extraction into Pydantic models
- Strong alignment with SemSQL architecture

### PydanticAI

- Typed AI agent systems
- Structured ontology extraction

### DeepOnto

- Ontology alignment
- Semantic embeddings
- AI-assisted ontology workflows

## Developer Tooling

### pytest

- Testing framework

### ty

- Static typing validation

### ruff

- Linting and formatting

### mkdocs-material

- Documentation platform
- Developer experience optimization

## Future Integrations

### Owlready2

- OWL reasoning support
- Ontology manipulation

### networkx

- Graph algorithms
- Graph traversal

### Polars

- DataFrame interoperability
- Typed ETL pipelines
- Ontology-aware DataFrame workflows

## Extras in pyproject.toml (0.1.0)

```toml
[project.optional-dependencies]
fastapi = ["fastapi>=0.100", "orjson>=3.9"]
dev = ["pytest", "pytest-cov", "ty", "ruff", "httpx", "fastapi", "orjson", ...]
```

- **`fastapi`** — installs FastAPI and orjson; `semsql.fastapi` uses orjson for JSON-LD responses when available
- **`dev`** — test, lint, and type-check tooling

Install examples:

```bash
pip install semsql
pip install semsql[fastapi]
pip install -e ".[dev]"
```

## Proposed future extras

The following are **not** yet defined in `pyproject.toml` but are under consideration:

```toml
jsonld = ["PyLD"]           # framing and advanced JSON-LD
shacl = ["pySHACL"]         # SHACL validation
graphdb = ["SPARQLWrapper", "neo4j"]
ai = ["instructor", "pydantic-ai", "deeponto"]
owl = ["Owlready2"]
polars = ["polars"]
```

## Strategic Recommendations

**Strongest foundational dependencies:**

- SQLModel
- Pydantic
- RDFLib

**Highest-value optional integrations:**

- FastAPI
- PyLD
- pySHACL
- Instructor

**Highest long-term strategic opportunities:**

- PydanticAI
- Polars
- Neo4j
- DeepOnto

SemSQL should expose Pythonic model-centric APIs rather than RDF-native APIs. RDFLib should remain an internal implementation detail wherever possible.
