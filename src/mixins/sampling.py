import logging
import math
from typing import Tuple, NewType, Dict, Any

from scipy.signal import resample_poly

from custom_types import Hz, Frames, FrameRange
from util.frames import to_frames
from util.math import rational_approximation

FilterCache = NewType("FilterCache", Dict[Tuple[Frames, Hz], Any])


class FIRResampler:
    def __init__(self):
        self.filter_cache: FilterCache = {}
        self.log = logging.getLogger(__name__)

    def get_temporal(self, fs: Hz, size: Frames, end: Frames):
        """Return a sample at the requested fs by resampling a static-fs buffer.

        1. Compute the "conversion factor" between requested fs and source fs.
        2. Compute a numerator and denominator approximating the conversion
        factor.
        3. Sample the source buffer.
        4. Upsample the source buffer by the conversion factor numerator.
        5. Downsample to upsampled buffer by the conversion factor denominator.
        """
        _L, _M = rational_approximation(fs / self._get_fs())
        conversion_factor = _L / _M
        # print(f"{self.data.uuid}: resampling {size} frames up to {end}")
        # print(f"Got L={_L} M={_M} for converting base {self._get_fs()} to {fs}")
        sample_size = math.ceil(size/conversion_factor)
        sample_end = end/conversion_factor
        # print(f"Sampling {sample_size} up to {sample_end}")
        buf = self._get_temporal(
            size=sample_size,
            end=sample_end,
        )
        # resample_poly does not have phase shift -> aliasing
        resampled = resample_poly(buf, up=_L, down=_M)
        # print(f"resampled buffer to {len(resampled)}")
        return resampled[:size]

    def get_range(self, fs: Hz) -> FrameRange:
        lower, upper = self._get_range()
        return (
                lower * fs / self._get_fs(),
                upper * fs / self._get_fs(),
        )

    def _get_fs(self) -> Frames:
        raise NotImplementedError

    def _get_temporal(self, start: Frames, end: Frames):
        raise NotImplementedError

    def _get_range(self) -> Tuple[Frames, Frames]:
        raise NotImplementedError
