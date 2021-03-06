from samplers.Sampler import Sampler
from custom_types import Seconds, Frames


class DilatedSampler(Sampler):
    def __init__(self, factor: float, parent: Sampler):
        Sampler.__init__(self, parent)
        self.factor = float(factor)

    def sample_out(self, source, fs, offset: Seconds, duration: Frames):
        return self.parent.sample_out(source, fs, self.factor * offset, duration)
