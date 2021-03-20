from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import FrameRange, Hz, Partial
from mixins.buffers import TilingMixin
from mixins.domains import TemporalDomainHelper
from util.buffer import get_centered_sample


class TiledSignal(TilingMixin, TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TemporalDomainHelper.__init__(self)
        TilingMixin.__init__(self)
        self.child = self.data.resolved_refs['child']
        self.direction = self.data.data['direction']

        if self.direction not in ['forward', 'backward', 'both']:
            raise ValueError(f"Given direction {self.direction} is not valid")

    def get_range(self, fs: Hz) -> FrameRange:
        lower, upper = self.child.get_range(fs)
        if self.direction == 'forward':
            return lower, None
        elif self.direction == 'backward':
            return None, upper
        else:
            return None, None

    def get_period(self, fs: Hz) -> Partial:
        return self.child.get_period(fs)

    def get_buffer(self, fs: Hz):
        return get_centered_sample(self.child, fs)


register(
    name="tiled",
    ctor=TiledSignal,
)
