import math

import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from custom_types import Hz, Frames, FrameRange
from mixins.sampling import FIRResampler
from util.frames import to_frames


class StreamingSignal(FIRResampler, Signal):
    def __init__(self, context: SignalContext):
        FIRResampler.__init__(self)
        Signal.__init__(self, context)
        self.source_fs = int(self.data.data['source_fs'])
        self.buf = np.zeros(self.source_fs * 10)
        self.dur = 0

    def _get_fs(self) -> Frames:
        return self.source_fs

    def _get_temporal(self, size: Frames, end: Frames):
        # # TODO: handle different fs gracefully
        # if fs != self.source_fs:
        #     raise ValueError(
        #         f"StreamingSignal {self.data.uuid} must be sampled "
        #         f" at {self.source_fs} frames/s"
        #     )
        if to_frames(end) > self.dur:
            raise ValueError(
                f"StreamingSignal {self.data.uuid} sampled for {size} up to {end} "
                f"with only {self.dur} frames available."
            )
        out = np.zeros(size)
        buf_start = max(math.ceil(end-size), 0)
        padding = buf_start - math.ceil(end-size)
        out[padding:padding+to_frames(end)-buf_start] = self.buf[buf_start:to_frames(end)]
        return out

    def get_spectral(self, fs: Hz):
        raise RuntimeError("Streaming signal does not allow spectral analysis")

    def _get_range(self) -> FrameRange:
        # # TODO: handle different fs gracefully
        # if fs != self.source_fs:
        #     raise ValueError(
        #         f"StreamingSignal {self.data.uuid} must be sampled "
        #         f" at {self.source_fs} frames/s"
        #     )
        return 0, self.dur

    def put_data(self, start, end, buf):
        cur_size = len(self.buf)
        if end > cur_size:
            new_buf = np.zeros(cur_size*2)
            new_buf[0:cur_size] = self.buf[:]
            self.buf = new_buf
        self.buf[start:end] = buf
        self.dur = max(self.dur, end)
