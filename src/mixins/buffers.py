from math import ceil

import numpy as np

from custom_types import Frames, FrameRange, Hz, Partial
from util.frames import to_frames, to_bufsize


class TilingMixin:
    """Utility mixin for finite signals which are zero-valued when out of range.

    Subclasses must implement `get_buffer`, which TilingMixin uses to provide a
    `get_temporal` implementation with the following behavior:
    * Tiling of buffer data according to `get_range`
    Support for signals which are unbounded in either direction.
    @DynamicAttrs
    """
    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        period = self.get_period(fs)
        source_buffer = self.get_buffer(fs)
        lower, upper = self.get_range(fs)

        # TODO: upsample source buffer to near-integer period
        if len(source_buffer) != to_bufsize(period):
            raise ValueError(
                f"Buffer returned for tiling has length {len(source_buffer)} "
                f"which is not suitable for period {period}"
            )

        # compute the sampleable range of the signal
        sample_end = to_frames(end if upper is None else min(upper, end))
        sample_start = to_frames(start if lower is None else max(lower, start))

        # tile the buffer enough to cover the sampleable range
        n_tiles = ceil(abs(sample_end-sample_start-start)/len(source_buffer))

        # rotate the tiled buffer into the same index space as the output
        tiled_buffer = np.roll(np.tile(source_buffer, n_tiles+1), -start)

        output_start = sample_start - start
        output_end = sample_end - start

        out = np.zeros(end-start)
        out[output_start:output_end] = tiled_buffer[output_start:output_end]

        return out

    def get_buffer(self, fs: Hz):
        """Get the buffer to tile.
        * Length should be equal to the period
        * Should be 0-based: original_index % period == 0 for buffer[0]
        """
        raise NotImplementedError


class DilatingMixin(TilingMixin):
    def get_buffer(self, fs: Hz):
        buffer = self.get_source_buffer()
        if fs == self.get_source_fs():
            # TODO: Investigate tolerances here
            # Some small differences in frame rate will not affect result.
            return buffer
        x = np.linspace(0, 1, to_bufsize(self.get_duration(fs)))
        xp = np.linspace(0, 1, len(buffer))
        return np.interp(x, xp, buffer)

    def get_duration(self, fs: Hz) -> Partial:
        return len(self.get_source_buffer()) * fs / self.get_source_fs()

    def get_period(self, fs: Hz) -> Partial:
        return self.get_duration(fs)

    def get_range(self, fs: Hz) -> FrameRange:
        return 0, self.get_duration(fs)

    def get_source_buffer(self):
        raise NotImplementedError

    def get_source_fs(self) -> Partial:
        raise NotImplementedError
