import numpy as np

from custom_types import Frames


class TilingMixin:
    """Utility mixin for finite signals which are zero-valued when out of range.

    Subclasses must implement `get_buffer`, which TilingMixin uses to provide a
    `get_temporal` implementation with the following behavior:
    * Tiling of buffer data according to `get_range`
    Support for signals which are unbounded in either direction.
    @DynamicAttrs
    """
    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        buffer = self.get_buffer(fs)
        lower, upper = self.get_range(fs)

        buf_start = 0 if lower is None else max(lower, 0)
        buf_end = len(buffer) if upper is None else min(upper, len(buffer))

        source_buffer = buffer[buf_start:buf_end]
        sample_end = end if upper is None else min(upper, end)
        sample_start = start if lower is None else max(lower, start)
        n_tiles = int((sample_end-sample_start)/len(source_buffer))+1
        tiled_buffer = np.roll(np.tile(source_buffer, n_tiles), buf_start-start)

        output_start = sample_start - start
        output_end = sample_end - start

        out = np.zeros(end-start)
        out[output_start:output_end] = tiled_buffer[output_start:output_end]

        return out

    def get_buffer(self, fs: Frames):
        raise NotImplementedError
