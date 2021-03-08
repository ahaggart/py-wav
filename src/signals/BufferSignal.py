import numpy as np

from Signal import Signal
from SignalData import SignalData
from custom_types import Frames, FrameRange
from mixins.buffers import TilingMixin, DilatingMixin
from mixins.domains import TemporalDomainHelper


class BufferSignal(DilatingMixin, TemporalDomainHelper, Signal):
    def __init__(self, data: SignalData):
        Signal.__init__(self, data)
        TemporalDomainHelper.__init__(self)
        TilingMixin.__init__(self)

        self.buffer = np.array(self.data.data['buffer'], dtype=float)
        self.fs = int(self.data.data['fs'])

    def get_source_buffer(self):
        return self.buffer

    def get_source_fs(self):
        return self.fs
