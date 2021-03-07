from __future__ import annotations

from typing import List, Dict

from Signal import Signal
from custom_types import Frames, FrameRange


class WrapperSignal(Signal):
    def __init__(self, ref: str, manager: SignalManager):
        Signal.__init__(self, None, None)
        self.manager = manager
        self.ref = ref
        self.child = None

    def get_child(self) -> Signal:
        if self.child is None:
            self.child = self.manager._get_signal(self.ref)
        return self.child

    def get_range(self, fs: Frames) -> FrameRange:
        return self.get_child().get_range(fs)

    def get_spectral(self, fs: Frames):
        return self.get_child().get_spectral(fs)

    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        return self.get_child().get_temporal(fs, start, end)

    def get_period(self, fs: Frames) -> Frames:
        return self.get_child().get_period(fs)


class SignalManager:
    def __init__(self):
        self.signals = None
        self.references = {}

    def setup(self, signals: List[Signal]):
        self.signals = {signal.data.uuid: signal for signal in signals}

    def get_signal(self,
                   uuid: str,
                   caller_uuid: str,
                   primary_domain: str = None) -> Signal:
        return WrapperSignal(uuid, self)

    def _get_signal(self, uuid: str) -> Signal:
        return self.signals[uuid]
