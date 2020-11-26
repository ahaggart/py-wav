from SourceState import SourceState
from core.Stateful import Stateful
from custom_types import Frames, Seconds
from samplers.Sampler import Sampler


class Source(Stateful):
    def __init__(self):
        Stateful.__init__(self)
        self.sampler = None
        self.state: SourceState = None

    def set_sampler(self, sampler: Sampler):
        self.sampler = sampler

    def sample(self, fs: Frames, offset: Seconds, start: Frames, end: Frames):
        self_frames = self.state.offset * fs
        sample_frames = offset * fs
        start_frame = int(sample_frames - self_frames) + start
        end_frame = int(sample_frames - self_frames) + end
        return self.get_buffer(fs, start_frame, end_frame)

    def get_buffer(self, fs: Frames, start: Frames, end: Frames):
        """Get the Source buffer at the given sample rate and frame range.
        """
        raise NotImplementedError

    def get_period(self, fs: Frames) -> Frames:
        raise NotImplementedError

    def get_duration(self, fs) -> int:
        """Get the Source duration. Deprecated.
        """
        return None
