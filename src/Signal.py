from __future__ import annotations

import SignalContext
from custom_types import Frames, FrameRange, Hz, Partial


class Signal:
    def __init__(self, context: SignalContext.SignalContext):
        self.data = context

    def get_temporal(self, start: Frames, end: Frames):
        raise NotImplementedError

    def get_spectral(self):
        raise NotImplementedError

    def get_range(self) -> FrameRange:
        raise NotImplementedError

    def get_fs(self):
        raise NotImplementedError
