# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-16

### Added

- `onto_field()` — SQLModel field helper with ontology metadata in `json_schema_extra`
- `onto_model()` — class decorator for `@type` and IRI templates
- `OntoMixin` — `to_jsonld()` and `to_rdf()` instance methods
- `PrefixRegistry` — CURIE expansion, compaction, and JSON-LD `@context` building
- JSON-LD export with `@context`, `@id`, `@type`, and nested model support
- RDF export (Turtle, JSON-LD, N-Triples, RDF/XML) via RDFLib
- Optional `semsql[fastapi]` extra: response classes and `Accept` header negotiation
- Example FastAPI app in `examples/fastapi_demo.py`

[0.1.0]: https://github.com/semsql/semsql/releases/tag/v0.1.0
