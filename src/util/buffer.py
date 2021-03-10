from math import floor, ceil

import numpy as np

from Signal import Signal
from custom_types import Partial, FrameRange, Hz, Frames
from util.frames import to_frames, to_bufsize


def get_valid_range(period: Partial,
                    frame_range: FrameRange) -> (Frames, Frames):
    lower, upper = frame_range
    bufsize = to_bufsize(period)
    if lower is not None:
        return to_frames(lower), to_frames(lower) + bufsize
    elif upper is not None:
        return to_frames(upper) - bufsize, to_frames(upper)
    else:
        return 0, bufsize


def get_centered_sample(signal: Signal, fs: Hz):
    lower, upper = get_valid_range(signal.get_period(fs), signal.get_range(fs))
    return np.roll(signal.get_temporal(fs, lower, upper), lower)
