from typing import Optional

import numpy as np
import simpleaudio as sa

from Signal import Signal
from custom_types import Frames
from sources.Source import Source
from util.frames import to_frames


def play_from_buffer(fs: Frames, buffer):
    # Ensure that highest value is in 16-bit range
    audio = buffer / np.max(np.abs(buffer)) * (2 ** 15 - 1)

    # Convert to 16-bit data
    audio = audio.astype(np.int16)

    # Start playback
    play_obj = sa.play_buffer(audio, 1, 2, fs)

    # Wait for playback to finish before exiting
    play_obj.wait_done()


def play_from_source(root: Source,
                     fs: int,
                     start: Optional[Frames] = None,
                     end: Optional[Frames] = None):
    start = start if start is not None else 0
    end = end if end is not None else root.get_duration(fs)
    buffer = root.get_buffer(fs, start, end)

    # Ensure that highest value is in 16-bit range
    audio = buffer / np.max(np.abs(buffer)) * (2**15 - 1)

    # Convert to 16-bit data
    audio = audio.astype(np.int16)

    # Start playback
    play_obj = sa.play_buffer(audio, 1, 2, fs)

    # Wait for playback to finish before exiting
    play_obj.wait_done()


def play_signal(signal: Signal,
                fs: int,
                start: Optional[Frames] = None,
                end: Optional[Frames] = None):
    start = to_frames(start if start is not None else 0)
    end = to_frames(end if end is not None else signal.get_range(fs)[1])
    buffer = signal.get_temporal(fs, start, end)

    # Ensure that highest value is in 16-bit range
    audio = buffer / np.max(np.abs(buffer)) * (2 ** 15 - 1)

    # Convert to 16-bit data
    audio = audio.astype(np.int16)

    # Start playback
    play_obj = sa.play_buffer(audio, 1, 2, fs)

    # Wait for playback to finish before exiting
    play_obj.wait_done()
