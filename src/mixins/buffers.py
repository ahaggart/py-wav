import numpy as np

from custom_types import Frames, FrameRange


class TilingMixin:
    """Utility mixin for finite signals which are zero-valued when out of range.

    Subclasses must implement `get_buffer`, which TilingMixin uses to provide a
    `get_temporal` implementation with the following behavior:
    * Tiling of buffer data according to `get_range`
    Support for signals which are unbounded in either direction.
    @DynamicAttrs
    """
    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        source_buffer = self.get_buffer(fs)
        lower, upper = self.get_range(fs)

        if len(source_buffer) != self.get_period(fs):
            raise ValueError(
                f"Buffer returned for tiling has length {len(source_buffer)} "
                f"which does not equal the period {self.get_period(fs)}"
            )

        # compute the sampleable range of the signal
        sample_end = end if upper is None else min(upper, end)
        sample_start = start if lower is None else max(lower, start)

        # tile the buffer enough to cover the sampleable range
        n_tiles = int((sample_end-sample_start)/len(source_buffer))+1

        # rotate the tiled buffer into the same index space as the output
        tiled_buffer = np.roll(np.tile(source_buffer, n_tiles), -start)

        output_start = sample_start - start
        output_end = sample_end - start

        out = np.zeros(end-start)
        out[output_start:output_end] = tiled_buffer[output_start:output_end]

        return out

    def get_buffer(self, fs: Frames):
        """Get the buffer to tile.
        * Length should be equal to the period
        * Should be 0-based: original_index % period == 0 for buffer[0]
        """
        raise NotImplementedError


class DilatingMixin(TilingMixin):
    def get_buffer(self, fs: Frames):
        buffer = self.get_source_buffer()
        if fs == self.get_source_fs():
            return buffer
        x = np.linspace(0, 1, self.get_duration(fs))
        xp = np.linspace(0, 1, len(buffer))
        return np.interp(x, xp, buffer)

    def get_duration(self, fs: Frames) -> Frames:
        return int((len(self.get_source_buffer()) * fs) / self.get_source_fs())

    def get_period(self, fs: Frames) -> Frames:
        return self.get_duration(fs)

    def get_range(self, fs: Frames) -> FrameRange:
        return 0, self.get_duration(fs)

    def get_source_buffer(self):
        raise NotImplementedError

    def get_source_fs(self):
        raise NotImplementedError
