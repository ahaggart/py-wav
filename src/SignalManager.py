from __future__ import annotations

from typing import List, Dict, Type

import Signal
from SignalCache import SignalCache
from SignalData import SignalData
from SignalGraph import SignalGraph


class SignalManager:
    def __init__(self, graph: SignalGraph, cache: SignalCache):
        self.signals = {}
        self.cache = cache
        self.graph = graph
        self.references = {}

    def setup(self,
              initializers: Dict[str, Type[Signal]],
              signal_data: List[SignalData]):
        for data in signal_data:
            data.set_refs(self.cache.resolve_refs(data.raw_refs))
            initializer = initializers[data.type_name]
            signal = initializer(data)
            self.signals[data.uuid] = signal

    def get_signal(self,
                   uuid: str,
                   caller_uuid: str,
                   primary_domain: str = None) -> Signal.Signal:
        return Signal.WrapperSignal(uuid, self)

    def _get_signal(self, uuid: str) -> Signal.Signal:
        return self.signals[uuid]


