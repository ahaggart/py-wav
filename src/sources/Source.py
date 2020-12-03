from SourceState import SourceState
from core.WithState import WithState
from core.WithUUID import WithUUID
from custom_types import Frames, Seconds


class Source(WithState, WithUUID):
    def __init__(self):
        WithState.__init__(self)
        WithUUID.__init__(self)

    def sample(self, fs: Frames, offset: Seconds, start: Frames, end: Frames):
        """Get the Source buffer at the given sample rate, offset, and range.

        sample() is a convenience method for converting frame ranges into the
        Source's own buffer space.

        offset is the ABSOLUTE offset in Seconds.

        We provide the start and end parameters in Frames rather than Seconds to
        ensure that we sample the expected number of frames. Both of these
        parameters are given as a distance in Frames from the offset time.
        """
        frame_offset = int((offset - self.state.offset) * fs)
        start_frame = frame_offset + start
        end_frame = frame_offset + end
        return self.get_buffer(fs, start_frame, end_frame)

    def get_buffer(self, fs: Frames, start: Frames, end: Frames):
        """Get the Source buffer at the given sample rate and frame range.

        The frame range [start:end] is given in buffer-space and is allowed to
        be arbitrary. Source subclasses are responsible for handling arbitrary
        frame ranges.

        For example, a Source class the populates its buffers from a .wav file
        has a finite amount of data in the backing file. The implementor must
        choose how to handle frame ranges outside the .wav file's data. This
        could be either (1) returning 0 for indices less than zero or greater
        than the backing file size, or (2) "rolling over" to the opposite end
        of the data, as if it repeated infinitely in either direction.

        The [0:period] is always expected to be in range. Analysis in non-time
        dimensions (ie FourierTransform) should query in this range to ensure
        no artifacts are introduced by out-of-range behavior.
        """
        raise NotImplementedError

    def get_period(self, fs: Frames) -> Frames:
        """Get the period in Frames of the Source at the given sample rate.

        Sources are required to specify a period to enable us to apply
        transforms requiring a full period of data. The range [0:period] is
        expected to be a safe range for calls to get_buffer.
        """
        raise NotImplementedError
