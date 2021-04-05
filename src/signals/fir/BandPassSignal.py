import numpy as np
from scipy.signal import firwin

from Signal import Signal
from SignalContext import SignalContext
from custom_types import Hz, Frames, FrameRange
from mixins.domains import TemporalDomainHelper
from mixins.sampling import FIRResampler


class BandPassSignal(FIRResampler, TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        FIRResampler.__init__(self)
        Signal.__init__(self, context)
        self.num_taps = int(self.data.data["num_taps"])
        self.band_start = Hz(self.data.data["band_start"])
        self.band_stop = Hz(self.data.data["band_stop"])
        self.child = self.data.resolved_refs["child"]
        self.window = self.data.data["window"]
        self.ht_cache = {}
        self.fs = int(self.data.data["fs"])
        self.ht = firwin(
                self.num_taps,
                cutoff=(self.band_start, self.band_stop),
                window=self.window,
                fs=self.fs,
                pass_zero='bandpass',
            )

    def _get_fs(self) -> Frames:
        return self.fs

    def _get_temporal(self, start: Frames, end: Frames):
        """Compute yt at the given points.
        convolve returns N + M - 1 samples
        [0:M-1] samples have lower boundary effect
        [N:N+M-1] samples have upper boundary effect

        In order to sample start:end without boundary effects:
        1. "back-pad" N by M-1
        2. drop last M-1 points
        """
        ht = self.ht

        # back-pad the sample to avoid boundary effects
        size = end - start
        sample_size = size + len(ht) - 1
        sample = self.child.get_temporal(self.fs, end-sample_size, end)
        conv = np.convolve(sample, ht)

        return conv[len(ht)-1:-(len(ht)-1)]

    def _get_range(self) -> FrameRange:
        return self.child.get_range(self.fs)
