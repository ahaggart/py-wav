from samplers.Sampler import Sampler
from custom_types import Seconds, Frames


class OffsetSampler(Sampler):
    def __init__(self, offset: Seconds, parent: Sampler):
        Sampler.__init__(self, parent)
        self.offset = offset

    def sample_out(self, source, fs, offset: Seconds, duration: Frames):
        return self.parent.sample_out(source, fs, offset + self.offset, duration)
