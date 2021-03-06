from SignalContext import SignalContext
from custom_types import Frames, FrameRange


class Signal:
    def __init__(self, context: SignalContext, data: dict):
        self.uuid = data['uuid']

    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        raise NotImplementedError

    def get_spectral(self, fs: Frames):
        raise NotImplementedError

    def get_period(self, fs: Frames) -> Frames:
        raise NotImplementedError

    def get_range(self, fs: Frames) -> FrameRange:
        raise NotImplementedError
