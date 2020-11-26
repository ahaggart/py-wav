from SourceState import SourceState
from custom_types import Frames
from sources.Source import Source


class DilatedSource(Source):
    def __init__(self, factor: float, child: Source):
        Source.__init__(self)
        self.factor = float(factor)
        self.child = child

    def get_buffer(self, fs, start, end):
        return self.child.get_buffer(
            fs=int(fs * self.factor),
            start=int(start * self.factor),
            end=int(end * self.factor),
        )

    def get_period(self, fs: Frames) -> Frames:
        return self.child.get_period(fs * self.factor)

    def set_state(self, state: SourceState):
        super().set_state(state)
        self.child.set_state(self.state.with_dilation(self.factor))
