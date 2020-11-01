from samplers.Sampler import Sampler
from custom_types import Seconds, Frames


class OffsetSampler(Sampler):
    def __init__(self, offset: Seconds, parent: Sampler):
        Sampler.__init__(self, parent)
        self.offset = offset

    def sample(self, source, fs, offset: Seconds, duration: Frames):
        return self.parent.sample(source, fs, offset+self.offset, duration)
