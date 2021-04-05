from math import ceil, floor

import numpy as np

from custom_types import Partial, Frames


def to_frames(partial: Partial) -> Frames:
    return round(partial)


def np_to_frames(buf):
    return np.round(buf).astype('int')


def to_bufsize(period: Partial) -> Frames:
    return round(period)
