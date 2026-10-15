"""Anklet graphs."""

from collections.abc import Hashable
from typing import Any
from anklet import Anklet


class AnkletGraph[T: Hashable]:
    """An **anklet graph** is a multi-hypergraph with additional combinatorial structure."""

    _name: str
    _node: dict[T, dict[str, Any]]
    _edge: dict[Anklet[T], int]

    def __init__(self, *, name: str = "") -> None:
        self._name = name
        self._node = {}
        self._edge = {}
