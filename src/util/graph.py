from typing import Dict

from Signal import Signal


def verify_fs(*args: Signal, **kwargs: Signal):
    pairs = []
    for name, child in kwargs.items():
        pairs.append((name, child.get_fs()))
    for idx, child in enumerate(args):
        pairs.append((idx, child.get_fs()))

    if len(set(map(lambda pair: pair[1], pairs))) > 1:
        raise ValueError(f"Child signals do not have matching FS: {pairs}")
