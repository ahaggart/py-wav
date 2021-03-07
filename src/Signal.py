from __future__ import annotations

import SignalContext
import SignalData
from custom_types import Frames, FrameRange


class Signal:
    def __init__(self, context: SignalContext.SignalContext, data: SignalData.SignalData):
        self.data = data
        self.context = context

    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        raise NotImplementedError

    def get_spectral(self, fs: Frames):
        raise NotImplementedError

    def get_period(self, fs: Frames) -> Frames:
        raise NotImplementedError

    def get_range(self, fs: Frames) -> FrameRange:
        raise NotImplementedError
