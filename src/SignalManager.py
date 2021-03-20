from __future__ import annotations

from typing import Dict

from Signal import Signal
from SignalCache import SignalCache, CachedSignal
from core.SignalProvider import SignalProvider


class SignalManager(SignalProvider):
    def __init__(self, cache: SignalCache):
        self.signals: Dict[str, Signal] = {}
        self.cache = cache
        self.cache_nodes: Dict[str, CachedSignal] = {}

    def put_signal(self, signal: Signal):
        self.signals[signal.data.uuid] = signal
        self.cache_nodes[signal.data.uuid] = CachedSignal(
            uuid=signal.data.uuid,
            cache=self.cache,
        )

    def get_signal(self, uuid: str) -> Signal:
        return self.signals[uuid]

    def resolve_ref(self, uuid: str) -> Signal:
        return self.cache_nodes[uuid]
