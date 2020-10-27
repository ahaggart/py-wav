import inspect
from typing import Dict

from samplers.Sampler import Sampler


class Source:
    def __init__(self):
        self.params = {}
        self.sampler = None

    def create_params(self):
        # do some magic to extract the constructor params
        caller_frame = inspect.stack()[1]
        arginfo = inspect.getargvalues(caller_frame[0])

        self.params = {arg: arginfo.locals[arg] for arg in arginfo.args if arg != 'self'}
        if arginfo.keywords is not None:
            self.params.update(arginfo.locals[arginfo.keywords])

    def set_sampler(self, sampler: Sampler):
        self.sampler = sampler

    def get_buffer(self, fs: int, start: int, end: int):
        raise NotImplementedError

    def get_duration(self, fs) -> int:
        raise NotImplementedError

    def get_params(self) -> Dict:
        return self.params.copy()
