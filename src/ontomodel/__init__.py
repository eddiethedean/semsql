"""OntoModel — semantic interoperability for SQLModel."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from ontomodel.decorator import apply_onto_model, onto_model
from ontomodel.fields import onto_field
from ontomodel.mixin import OntoMixin
from ontomodel.registry import PrefixRegistry

try:
    __version__ = version("ontomodel")
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
