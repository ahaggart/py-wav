from Signal import Signal
from SignalContext import SignalContext
from custom_types import Frames, FrameRange, Hz, Partial


class DerivedSignal(Signal):
    """Convenience class for Signals derived from other signals.
    """
    def __init__(self, context: SignalContext, child: str):
        Signal.__init__(self, context)
        self.child = self.data.resolved_refs[child]

    def get_spectral(self):
        return self.child.get_spectral()

    def get_temporal(self, start: Frames, end: Frames):
        return self.child.get_temporal(start, end)

    def get_range(self) -> FrameRange:
        return self.child.get_range()

    def get_fs(self) -> Frames:
        return self.child.get_fs()
