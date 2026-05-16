"""RDF serialization via RDFLib."""

from __future__ import annotations

import json
from typing import Any

from rdflib import Graph
from sqlmodel import SQLModel

from ontomodel.jsonld import model_to_jsonld

# User-facing format names -> rdflib serialization format
FORMAT_MAP: dict[str, str] = {
    "turtle": "turtle",
    "ttl": "turtle",
    "json-ld": "json-ld",
    "jsonld": "json-ld",
    "nt": "nt",
    "n-triples": "nt",
    "ntriples": "nt",
    "xml": "xml",
    "rdf+xml": "xml",
    "rdfxml": "xml",
}

MEDIA_TYPES: dict[str, str] = {
    "turtle": "text/turtle",
    "json-ld": "application/ld+json",
    "nt": "application/n-triples",
    "xml": "application/rdf+xml",
}


def normalize_format(fmt: str) -> str:
    """Normalize a format string to an rdflib serializer name."""
    key = fmt.lower().replace("_", "-")
    if key not in FORMAT_MAP:
        raise ValueError(
            f"Unsupported RDF format: {fmt!r}. "
            f"Supported: {', '.join(sorted(set(FORMAT_MAP.keys())))}"
        )
    return FORMAT_MAP[key]


def jsonld_to_graph(document: dict[str, Any]) -> Graph:
    """Parse a JSON-LD document into an rdflib Graph."""
    graph = Graph()
    graph.parse(data=json.dumps(document), format="json-ld")
    return graph


def model_to_graph(
    instance: SQLModel,
    *,
    registry: Any = None,
) -> Graph:
    """Convert a model instance to an rdflib Graph."""
    from ontomodel.registry import PrefixRegistry

    reg: PrefixRegistry | None = registry
    doc = model_to_jsonld(instance, registry=reg)
    return jsonld_to_graph(doc)


def serialize_graph(graph: Graph, fmt: str) -> str:
    """Serialize a graph to a string in the given format."""
    rdflib_fmt = normalize_format(fmt)
    serialized = graph.serialize(format=rdflib_fmt)
    return str(serialized)


def model_to_rdf(
    instance: SQLModel,
    *,
    format: str = "turtle",
    registry: Any = None,
) -> str:
    """Serialize a model instance to an RDF string."""
    graph = model_to_graph(instance, registry=registry)
    return serialize_graph(graph, format)


def media_type_for_format(fmt: str) -> str:
    """Return the HTTP media type for an RDF format name."""
    rdflib_fmt = normalize_format(fmt)
    return MEDIA_TYPES.get(rdflib_fmt, "application/octet-stream")
