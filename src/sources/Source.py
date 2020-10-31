import inspect
from typing import Dict

from mapper.Mappable import Mappable
from samplers.Sampler import Sampler


class Source(Mappable):
    def __init__(self):
        Mappable.__init__(self)
        self.create_mapping()
        self.sampler = None

    def set_sampler(self, sampler: Sampler):
        self.sampler = sampler

    def get_buffer(self, fs: int, start: int, end: int):
        raise NotImplementedError

    def get_duration(self, fs) -> int:
        raise NotImplementedError
