from samplers.Sampler import Sampler


class Source:
    def __init__(self):
        self.sampler = None

    def set_sampler(self, sampler: Sampler):
        self.sampler = sampler

    def get_buffer(self, fs: int, start: int, end: int):
        raise NotImplementedError

    def get_duration(self, fs) -> int:
        raise NotImplementedError
