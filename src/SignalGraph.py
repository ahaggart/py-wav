from __future__ import annotations

from Signal import Signal
from custom_types import Frames, FrameRange


class DummySignal(Signal):
    def __init__(self):
        Signal.__init__(self, None, None)
        self.child = None

    def set_child(self, child: Signal) -> None:
        self.child = child

    def get_range(self, fs: Frames) -> FrameRange:
        return self.child.get_range(fs)

    def get_spectral(self, fs: Frames):
        return self.child.get_spectral(fs)

    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        return self.child.get_temporal(fs, start, end)

    def get_period(self, fs: Frames) -> Frames:
        return self.child.get_period(fs)


class SignalGraphEdge:
    def __init__(self, from_uuid: str, to_uuid: str, domain: str):
        self.from_uuid = from_uuid
        self.to_uuid = to_uuid
        self.domain = domain


class SignalGraph:
    def __init__(self):
        self.edges = []

    def link(self, from_uuid: str, to_uuid: str, domain: str) -> Signal:
        edge = SignalGraphEdge(from_uuid, to_uuid, domain)
