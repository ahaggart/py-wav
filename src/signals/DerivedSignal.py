from Signal import Signal
from SignalData import SignalData
from custom_types import Frames, FrameRange


class DerivedSignal(Signal):
    """Convenience class for Signals derived from other signals.
    """
    def __init__(self, data: SignalData, child: str):
        Signal.__init__(self, data)
        self.child = self.data.resolved_refs[child]

    def get_spectral(self, fs: Frames):
        return self.child.get_spectral(fs)

    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        return self.child.get_temporal(fs, start, end)

    def get_period(self, fs: Frames) -> Frames:
        return self.child.get_period(fs)

    def get_range(self, fs: Frames) -> FrameRange:
        return self.child.get_range(fs)
