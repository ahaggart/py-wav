from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import FrameRange, Hz, Partial, Seconds
from mixins.buffers import TilingMixin
from mixins.domains import TemporalDomainHelper
from util.buffer import get_centered_sample
from util.frames import to_frames


class TiledSignal(TilingMixin, TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.child = self.data.resolved_refs['child']
        self.lower = Seconds(self.data.data['lower'])
        self.upper = Seconds(self.data.data['upper'])

    def get_range(self, fs: Hz) -> FrameRange:
        return to_frames(self.lower*fs), to_frames(self.upper*fs)

    def get_buffer(self, fs: Hz):
        return get_centered_sample(self.child, fs)


register(
    name="tiled",
    ctor=TiledSignal,
)
