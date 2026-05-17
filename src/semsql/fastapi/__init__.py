"""FastAPI integration (optional extra)."""

from __future__ import annotations

try:
    from semsql.fastapi.negotiate import negotiate_onto_response
    from semsql.fastapi.responses import (
        JSONLDResponse,
        NTriplesResponse,
        RDFResponse,
        RDFXMLResponse,
        TurtleResponse,
    )
except ImportError as exc:
    if "fastapi" in str(exc).lower() or "starlette" in str(exc).lower():
        raise ImportError(
            "FastAPI support requires the fastapi extra: pip install semsql[fastapi]"
        ) from exc
    raise

__all__ = [
    "JSONLDResponse",
    "NTriplesResponse",
    "RDFResponse",
    "RDFXMLResponse",
    "TurtleResponse",
    "negotiate_onto_response",
]
