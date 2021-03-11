from math import ceil

import numpy as np

from custom_types import Partial, Frames


def to_frames(partial: Partial) -> Frames:
    return ceil(partial)


def np_to_frames(buf):
    return np.ceil(buf).astype('int')


def to_bufsize(period: Partial) -> Frames:
    return round(period)
