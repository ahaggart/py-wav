from __future__ import annotations

import SignalData
from custom_types import Frames, FrameRange, Hz, Partial


class Signal:
    def __init__(self, data: SignalData.SignalData):
        self.data = data

    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        raise NotImplementedError

    def get_spectral(self, fs: Hz):
        raise NotImplementedError

    def get_period(self, fs: Hz) -> Partial:
        raise NotImplementedError

    def get_range(self, fs: Hz) -> FrameRange:
        raise NotImplementedError
