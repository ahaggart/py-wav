import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Partial, Frames, FrameRange
from mixins.buffers import TilingMixin, TruncatingMixin
from mixins.domains import TemporalDomainHelper


class BufferSignal(TruncatingMixin, TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TruncatingMixin.__init__(self)
        TilingMixin.__init__(self)

        self.buffer = np.array(self.data.data['buffer'], dtype=float)
        self.fs = int(self.data.data['fs'])

    def get_temporal_checked(self, start: Frames, end: Frames):
        return self.buffer[start:end]

    def get_range(self) -> FrameRange:
        return 0, len(self.buffer)

    def get_source_buffer(self):
        return self.buffer

    def get_fs(self) -> Partial:
        return self.fs


register(
    name="buffer",
    ctor=BufferSignal,
)
