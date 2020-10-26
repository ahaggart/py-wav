from samplers.Sampler import Sampler


class OffsetSampler(Sampler):
    def __init__(self, offset: float, parent: Sampler):
        Sampler.__init__(self, parent)
        self.offset = offset

    def sample(self, source, fs, start, end):
        offset_fs = int(self.offset*self.parent.get_fs())
        return self.parent.sample(source, fs, start+offset_fs, end+offset_fs)
