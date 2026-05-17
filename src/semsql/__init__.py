"""SemSQL — semantic interoperability for SQLModel."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from semsql.decorator import apply_onto_model, onto_model
from semsql.fields import onto_field
from semsql.mixin import OntoMixin
from semsql.registry import PrefixRegistry

try:
    __version__ = version("semsql")
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
