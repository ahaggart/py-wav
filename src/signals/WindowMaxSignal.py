import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from SignalContext import SignalContext
from custom_types import Hz, Frames
from mixins.domains import TemporalDomainHelper
from signals.DerivedSignal import DerivedSignal


class WindowMaxSignal(TemporalDomainHelper, DerivedSignal):
    def __init__(self, context: SignalContext):
        DerivedSignal.__init__(self, context, "child")
        self.length = float(self.data.data['length'])

    def get_temporal(self, fs: Hz, size: Frames, end: Frames):
        window_size = int(self.length * fs)
        sample_size = size + window_size - 1
        buf = np.abs(self.child.get_temporal(fs, sample_size, end))
        # print(f"{self.data.uuid} size={size} end={end} window_size={window_size} buf={len(buf)}")
        windowed = sliding_window_view(buf, window_size)
        return np.max(windowed, axis=1)
