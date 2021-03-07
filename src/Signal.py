from __future__ import annotations

from SignalData import SignalData
from custom_types import Frames, FrameRange


class Signal:
    def __init__(self, data: SignalData):
        self.data = data

    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        raise NotImplementedError

    def get_spectral(self, fs: Frames):
        raise NotImplementedError

    def get_period(self, fs: Frames) -> Frames:
        raise NotImplementedError

    def get_range(self, fs: Frames) -> FrameRange:
        raise NotImplementedError
