"""Base classes for Sampler structure allowing conversion between nested
Source coordinate systems."""
from custom_types import Seconds, Frames


class Sampler:
    def __init__(self, parent):
        self.parent = parent

    def sample_out(self, source, fs, offset: Seconds, duration: Frames):
        """Convert an in-source offset to an absolute offset."""
        return self.parent.sample_out(source, fs, offset, duration)


class RootSampler(Sampler):
    def __init__(self, fs):
        Sampler.__init__(self, self)
        self.fs = fs

    def sample_out(self, source, fs, offset: Seconds, duration: Frames):
        start = int(offset * fs)
        end = start + duration
        return source.get_buffer(fs, start, end)
