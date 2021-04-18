import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from custom_types import Hz, Frames, FrameRange
from mixins.sampling import ResampledSignal


class StreamingSignal(Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.fs = int(self.data.data['source_fs'])
        self.buf = np.zeros(self.fs * 10)
        self.dur = 0

    def get_fs(self) -> Frames:
        return self.fs

    def get_temporal(self, start: Frames, end: Frames):
        if end > self.dur:
            raise ValueError(
                f"StreamingSignal {self.data.uuid} sampled for {start} to {end} "
                f"with only {self.dur} frames available."
            )
        size = end - start
        out = np.zeros(size)
        if end < 0:
            return out
        sample_size = min(end, size)
        padding = size - sample_size
        out[padding:padding+sample_size] = self.buf[end-sample_size:end]
        return out

    def get_spectral(self):
        raise RuntimeError("Streaming signal does not allow spectral analysis")

    def get_range(self) -> FrameRange:
        return 0, self.dur

    def put_data(self, start, end, buf):
        cur_size = len(self.buf)
        if end > cur_size:
            new_buf = np.zeros(cur_size*2)
            new_buf[0:cur_size] = self.buf[:]
            self.buf = new_buf
        self.buf[start:end] = buf
        self.dur = max(self.dur, end)
