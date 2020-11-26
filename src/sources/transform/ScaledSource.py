from SourceState import SourceState
from custom_types import Frames
from parameters.Parameter import parametrize, Parametrizable
from sources.Source import Source


class ScaledSource(Source):
    def __init__(self, scale: Parametrizable, child: Source):
        Source.__init__(self)
        self.child = child
        self.scale = parametrize(scale)

    def set_state(self, state: SourceState):
        super().set_state(state)
        self.child.set_state(self.state)

    def get_buffer(self, fs: Frames, start: Frames, end: Frames):
        scaling = self.scale.sample(fs, self.state.offset, start, end)
        buf = self.child.get_buffer(fs, start, end)
        return buf * scaling

    def get_period(self, fs: Frames) -> Frames:
        return self.child.get_period(fs)
