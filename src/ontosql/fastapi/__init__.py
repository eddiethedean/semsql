"""FastAPI integration (optional extra).

Requires semantic instances with export methods (planned 0.2.x). Negotiation helpers
remain available for dict/str payloads and future OntoModel export.
"""

from __future__ import annotations

try:
    from ontosql.fastapi.negotiate import negotiate_onto_response
    from ontosql.fastapi.responses import (
        JSONLDResponse,
        NTriplesResponse,
        RDFResponse,
        RDFXMLResponse,
        TurtleResponse,
    )
except ImportError as exc:
    if "fastapi" in str(exc).lower() or "starlette" in str(exc).lower():
        raise ImportError(
            "FastAPI support requires the fastapi extra: pip install ontosql[fastapi]"
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
