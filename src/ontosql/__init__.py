"""OntoSQL — semantic interoperability for SQLModel."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from ontosql.decorator import apply_onto_model, onto_model
from ontosql.fields import onto_field
from ontosql.mixin import OntoMixin
from ontosql.registry import PrefixRegistry

try:
    __version__ = version("ontosql")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = [
    "OntoMixin",
    "PrefixRegistry",
    "__version__",
    "apply_onto_model",
    "onto_field",
    "onto_model",
]
