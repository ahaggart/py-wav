from __future__ import annotations

from SignalCache import SignalCache
from SignalGraph import SignalGraph


class SignalManager:
    def __init__(self, graph: SignalGraph, cache: SignalCache):
        self.signals = {}
        self.cache = cache
        self.graph = graph
        self.references = {}
