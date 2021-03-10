from math import ceil

from custom_types import Partial, Frames


def to_frames(partial: Partial) -> Frames:
    return ceil(partial)


def to_bufsize(period: Partial) -> Frames:
    return round(period)
