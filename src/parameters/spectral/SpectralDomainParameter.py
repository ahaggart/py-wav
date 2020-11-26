from SourceState import SourceState
from core.Stateful import Stateful
from custom_types import Frames


class SpectralDomainParameter(Stateful):
    def __init__(self):
        Stateful.__init__(self)

    def get_buffer(self, fs: Frames):
        raise NotImplementedError

    def get_period(self, fs: Frames) -> Frames:
        raise NotImplementedError

    def get_state(self) -> SourceState:
        raise NotImplementedError
