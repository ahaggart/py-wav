import numpy as np
from scipy.signal import firwin, hilbert

from Signal import Signal
from SignalContext import SignalContext
from custom_types import Hz, Frames, FrameRange
from mixins.domains import TemporalDomainHelper


class BandPassSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.num_taps = int(self.data.data["num_taps"])
        self.band_start = Hz(self.data.data["band_start"])
        self.band_stop = Hz(self.data.data["band_stop"])
        self.child = self.data.resolved_refs["child"]
        self.window = self.data.data["window"]
        self.ht_cache = {}

    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        """Compute yt at the given points.
        convolve returns N + M - 1 samples
        [0:M-1] samples have lower boundary effect
        [N:N+M-1] samples have upper boundary effect

        In order to sample start:end without boundary effects:
        1. "back-pad" N by M-1
        2. drop last M-1 points
        """
        if fs not in self.ht_cache:
            # TODO: nodes should not store any state
            self.ht_cache[fs] = firwin(
                self.num_taps,
                cutoff=(self.band_start, self.band_stop),
                window=self.window,
                fs=fs,
                pass_zero='bandpass',
            )
        ht = self.ht_cache[fs]

        # back-pad the sample to avoid boundary effects
        sample_start = start - len(ht) + 1
        sample = self.child.get_temporal(fs, sample_start, end)
        conv = np.convolve(sample, ht)

        return conv[len(ht)-1:-len(ht)+1]

    def get_range(self, fs: Hz) -> FrameRange:
        return self.child.get_range(fs)
