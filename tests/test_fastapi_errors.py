"""FastAPI response error paths."""

from __future__ import annotations

import pytest

from semsql.fastapi.responses import RDFResponse


def test_invalid_response_data() -> None:
    with pytest.raises(TypeError, match="Response data must"):
        RDFResponse(12345)
