from samplers.Sampler import Sampler


class DilatedSampler(Sampler):
    def __init__(self, factor: float, parent: Sampler):
        Sampler.__init__(self, parent)
        self.factor = float(factor)

    def get_fs(self):
        return int(self.factor*self.parent.get_fs())
