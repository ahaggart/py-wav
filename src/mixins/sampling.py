import logging
import math
from typing import Tuple, NewType, Dict, Any

import numpy as np
from scipy.signal import resample_poly, firwin, upfirdn

from Signal import Signal
from SignalContext import SignalContext
from custom_types import Hz, Frames, FrameRange
from mixins.domains import TemporalDomainHelper
from util.frames import to_frames
from util.math import rational_approximation

FilterCache = NewType("FilterCache", Dict[Tuple[Frames, Hz], Any])


class ResampledSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.filter_cache: FilterCache = {}
        self.log = logging.getLogger(__name__)
        self.ht_cache = {}
        self.child = self.data.resolved_refs['child']
        self.target_fs = self.data.data['target_fs']
        self.source_fs = self.child.get_fs()

    def get_temporal(self, start: Frames, end: Frames):
        """Return a sample at the requested fs by resampling a static-fs buffer.

        1. Compute the "conversion factor" between requested fs and source fs.
        2. Compute a numerator and denominator approximating the conversion
        factor.
        3. Sample the source buffer.
        4. Upsample the source buffer by the conversion factor numerator.
        5. Downsample to upsampled buffer by the conversion factor denominator.
        
        
        source      | X--X--X--X--X--X--
        upsampled   | X00X00X00X00X00X00
        downsampled | X-0-0-X-0-0-X-0-0-

        centering: when working across fs-spaces, assume blocks start at 0
        ex: request 2-12 @ fs=4 from a 2up/3down resampler
        1-11@4 maps to 3-33@12 maps to 1.5-16.5@6

        1. sample 1-17@6
        2. upsample to 2-34@12
        3. downsample 3,6,9,12,15,18,21,24,27,30,33 -> 1-11

        """
        size = end - start
        num_taps = 100
        if self.target_fs == self.source_fs:
            return self.child.get_temporal(start, end)
        _L, _M = rational_approximation(self.target_fs / self.source_fs)
        target_nyq = self.target_fs / 2
        source_nyq = self.source_fs / 2
        nyq = min(target_nyq, source_nyq)
        if nyq not in self.ht_cache:
            self.ht_cache[nyq] = firwin(
                numtaps=num_taps,
                cutoff=nyq,
                fs=self.source_fs * _L,
            )
        ht = self.ht_cache[nyq]
        filter_pad = (num_taps-1)
        m_start = start * _M - filter_pad  # back-sampling

        # we only need the first frame of the last block
        # thus we subtract (_M - 1) frames from the end
        m_end = (end - 1) * _M + 1  # <-> end * _M - (_M - 1)

        l_start = math.floor(m_start / _L)
        l_end = math.ceil(m_end / _L)

        # compute the decimation indices the l-buffer
        m_offset = m_start - l_start * _L
        m_size = size * _M

        buf = self.child.get_temporal(l_start, l_end)
        l_buf = np.zeros(_L * len(buf))
        l_buf[::_L] = buf
        l_filtered = np.convolve(ht, l_buf)[filter_pad:-filter_pad]
        m_buf = l_filtered[m_offset:m_offset+m_size:_M]

        return m_buf

    def get_fs(self) -> Frames:
        return self.target_fs

    def get_range(self) -> FrameRange:
        lower, upper = self.child.get_range()
        factor = self.target_fs / self.source_fs
        return lower*factor, upper*factor
