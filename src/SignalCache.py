from __future__ import annotations
from typing import List, Dict, Type

from Signal import Signal
from SignalData import SignalData
from custom_types import Frames, FrameRange


class CachedSignal(Signal):
    def __init__(self, uuid: str, cache: SignalCache):
        Signal.__init__(self, None)
        self.uuid = uuid
        self.cache = cache
        self.child = None

    def get_child(self) -> Signal:
        if self.child is None:
            self.child = self.cache.get_signal(self.uuid)
        return self.child

    def get_range(self, fs: Frames) -> FrameRange:
        return self.get_child().get_range(fs)

    def get_spectral(self, fs: Frames):
        return self.cache.get_spectral(self.uuid, fs)

    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        return self.cache.get_temporal(self.uuid, fs, start, end)

    def get_period(self, fs: Frames) -> Frames:
        return self.get_child().get_period(fs)


class SignalCache:
    def __init__(self,
                 initializers: Dict[str, Type[Signal]],
                 signal_data: List[SignalData]):
        self.temporal = {}
        self.spectral = {}
        self.cache_nodes = self.create_cache_nodes(signal_data)
        self.signals = self.create_signals(initializers, signal_data)

    def create_cache_nodes(self,
                           signal_data: List[SignalData]
                           ) -> Dict[str, CachedSignal]:
        cache_nodes = {}
        for data in signal_data:
            cache_nodes[data.uuid] = CachedSignal(data.uuid, self)
        return cache_nodes

    def create_signals(self,
                       initializers: Dict[str, Type[Signal]],
                       signal_data: List[SignalData]):
        signals = {}
        for data in signal_data:
            data.set_refs(self.resolve_refs(data.raw_refs))
            initializer = initializers[data.type_name]
            signal = initializer(data)
            if data.uuid in signals:
                raise KeyError(f"Duplicate UUID {data.uuid} in signals")
            signals[data.uuid] = signal
        return signals

    def resolve_refs(self, raw_refs: Dict[str, str]) -> Dict[str, Signal]:
        return {name: self.cache_nodes[uuid] for name, uuid in raw_refs.items()}

    def get_cache_node(self, uuid: str):
        if uuid not in self.cache_nodes:
            self.cache_nodes[uuid] = CachedSignal(uuid, self)
        return self.cache_nodes[uuid]

    def get_signal(self, uuid: str):
        return self.signals[uuid]

    def get_temporal(self, uuid: str, fs: Frames, start: Frames, end: Frames):
        return self.get_signal(uuid).get_temporal(fs, start, end)

    def get_spectral(self, uuid: str, fs: Frames):
        return self.get_signal(uuid).get_spectral(fs)
