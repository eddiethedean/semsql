"""Content negotiation for OntoModel FastAPI routes."""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from ontomodel.fastapi.responses import (
    JSONLDResponse,
    NTriplesResponse,
    RDFXMLResponse,
    TurtleResponse,
)

# MIME type -> response factory
_ACCEPT_MAP: list[tuple[str, type[Response]]] = [
    ("application/ld+json", JSONLDResponse),
    ("text/turtle", TurtleResponse),
    ("application/n-triples", NTriplesResponse),
    ("application/rdf+xml", RDFXMLResponse),
]


def _parse_accept(accept: str | None) -> str | None:
    """Return the best matching semantic media type from Accept header."""
    if not accept:
        return None
    candidates: list[tuple[float, str]] = []
    for part in accept.split(","):
        part = part.strip()
        if not part:
            continue
        if ";q=" in part:
            mime, _, qval = part.partition(";q=")
            try:
                q = float(qval.strip())
            except ValueError:
                q = 1.0
        else:
            mime = part
            q = 1.0
        mime = mime.strip().lower()
        for known_mime, _ in _ACCEPT_MAP:
            if mime == known_mime or mime == "*/*" or mime == "application/*":
                candidates.append((q, known_mime))
        for known_mime, _ in _ACCEPT_MAP:
            if mime in known_mime:
                candidates.append((q * 0.9, known_mime))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def negotiate_onto_response(request: Request, data: Any) -> Response:
    """
    Return a FastAPI Response based on the request Accept header.

    Falls back to JSON-LD if data supports ``to_jsonld()``, otherwise JSON.
    """
    chosen = _parse_accept(request.headers.get("accept"))
    if chosen is None:
        if hasattr(data, "to_jsonld"):
            return JSONLDResponse(data)
        if isinstance(data, dict):
            return JSONLDResponse(data)
        return JSONResponse(content=data)

    for mime, response_cls in _ACCEPT_MAP:
        if mime == chosen:
            return response_cls(data)

    return JSONLDResponse(data)
