from custom_types import Seconds, Frames


class Sampler:
    def __init__(self, parent):
        self.parent = parent

    def sample(self, source, fs, offset: Seconds, duration: Frames):
        return self.parent.sample(source, fs, offset, duration)


class RootSampler(Sampler):
    def __init__(self, fs):
        Sampler.__init__(self, self)
        self.fs = fs

    def sample(self, source, fs, offset: Seconds, duration: Frames):
        start = int(offset * fs)
        end = start + duration
        return source.get_buffer(fs, start, end)
