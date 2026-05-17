"""RDF serialization format helpers (for FastAPI until full export lands)."""

from __future__ import annotations

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
    key = fmt.lower().replace("_", "-")
    if key not in FORMAT_MAP:
        raise ValueError(
            f"Unsupported RDF format: {fmt!r}. "
            f"Supported: {', '.join(sorted(set(FORMAT_MAP.values())))}"
        )
    return FORMAT_MAP[key]


def media_type_for_format(fmt: str) -> str:
    return MEDIA_TYPES[normalize_format(fmt)]
