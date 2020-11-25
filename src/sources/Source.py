from SourceState import SourceState
from core.Stateful import Stateful
from samplers.Sampler import Sampler


class Source(Stateful):
    def __init__(self):
        Stateful.__init__(self)
        self.create_mapping()
        self.sampler = None
        self.state: SourceState = None

    def set_sampler(self, sampler: Sampler):
        self.sampler = sampler

    def get_buffer(self, fs: int, start: int, end: int):
        raise NotImplementedError

    def get_duration(self, fs) -> int:
        raise NotImplementedError
