import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from custom_types import Hz, Frames, FrameRange


class StreamingSignal(Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.source_fs = int(self.data.data['source_fs'])
        self.buf = np.zeros(self.source_fs * 10)
        self.dur = 0

    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        # TODO: handle different fs gracefully
        if fs != self.source_fs:
            raise ValueError(
                f"StreamingSignal {self.data.uuid} must be sampled "
                f" at {self.source_fs} frames/s"
            )
        if end > self.dur:
            raise ValueError(
                f"StreamingSignal {self.data.uuid} sampled for {start}-{end} "
                f"with only {self.dur} frames available."
            )
        out = np.zeros(end-start)
        buf_start = max(start, 0)
        padding = buf_start - start
        out[padding:padding+end-start] = self.buf[buf_start:end]
        return out

    def get_spectral(self, fs: Hz):
        raise RuntimeError("Streaming signal does not allow spectral analysis")

    def get_range(self, fs: Hz) -> FrameRange:
        # TODO: handle different fs gracefully
        if fs != self.source_fs:
            raise ValueError(
                f"StreamingSignal {self.data.uuid} must be sampled "
                f" at {self.source_fs} frames/s"
            )
        return 0, self.dur

    def put_data(self, buf):
        self.buf[self.dur:self.dur+len(buf)] = buf
        self.dur += len(buf)
