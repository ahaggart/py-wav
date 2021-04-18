import math

import numpy as np
from scipy.signal import firwin

from Signal import Signal
from SignalContext import SignalContext
from custom_types import Hz, Frames, FrameRange
from mixins.domains import TemporalDomainHelper
from mixins.sampling import ResampledSignal
from util.math import rational_approximation


class BandPassSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.num_taps = int(self.data.data["num_taps"])
        self.band_start = Hz(self.data.data["band_start"])
        self.band_stop = Hz(self.data.data["band_stop"])
        self.child = self.data.resolved_refs["child"]
        self.window = self.data.data["window"]
        self.ht_cache = {}
        self.target_fs = int(self.data.data["fs"])
        self.ht = firwin(
                self.num_taps,
                cutoff=(self.band_start, self.band_stop),
                window=self.window,
                fs=self.target_fs,
                pass_zero='bandpass',
            )

    def get_fs(self) -> Frames:
        return self.child.get_fs()

    def get_temporal(self, start: Frames, end: Frames):
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
        sample = self.child.get_temporal(end-sample_size, end)
        conv = np.convolve(sample, ht)

        return conv[len(ht)-1:-(len(ht)-1)]

    def get_range(self) -> FrameRange:
        return self.child.get_range()
