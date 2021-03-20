import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register, RegistryEntry
from custom_types import Frames, FrameRange, Partial
from mixins.buffers import TilingMixin, DilatingMixin
from mixins.domains import TemporalDomainHelper


class BufferSignal(DilatingMixin, TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TemporalDomainHelper.__init__(self)
        TilingMixin.__init__(self)

        self.buffer = np.array(self.data.data['buffer'], dtype=float)
        self.fs = int(self.data.data['fs'])

    def get_source_buffer(self):
        return self.buffer

    def get_source_fs(self) -> Partial:
        return self.fs


register(
    name="buffer",
    ctor=BufferSignal,
)
