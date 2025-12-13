"""Preset refining strategies for common use cases."""

from .aggressive import AggressiveStrategy
from .minimal import MinimalStrategy
from .standard import StandardStrategy

__all__ = [
    "MinimalStrategy",
    "StandardStrategy",
    "AggressiveStrategy",
]
