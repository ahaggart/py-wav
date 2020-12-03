from SourceState import SourceState
from core.WithState import WithState
from core.WithUUID import WithUUID
from custom_types import Frames


class SpectralDomainParameter(WithState, WithUUID):
    def __init__(self):
        WithState.__init__(self)
        WithUUID.__init__(self)

    def get_buffer(self, fs: Frames):
        raise NotImplementedError

    def get_period(self, fs: Frames) -> Frames:
        raise NotImplementedError

    def get_state(self) -> SourceState:
        raise NotImplementedError
