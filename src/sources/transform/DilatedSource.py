from samplers.Sampler import Sampler
from sources.Source import Source


class DilatedSource(Source):
    def __init__(self, factor: float, child: Source, **kwargs):
        Source.__init__(self)
        self.create_mapping()
        self.factor = float(factor)
        self.child = child

    def get_buffer(self, fs, start, end):
        return self.child.get_buffer(
            fs=int(fs * self.factor),
            start=int(start * self.factor),
            end=int(end * self.factor),
        )

    def get_duration(self, fs):
        return self.child.get_duration(fs * self.factor)

    def set_sampler(self, sampler: Sampler):
        super().set_sampler(sampler)
        self.child.set_sampler(sampler)
