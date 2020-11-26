from typing import Optional

import numpy as np
import simpleaudio as sa

from custom_types import Frames
from samplers.Sampler import RootSampler
from sources.Source import Source


def play_from_source(root: Source,
                     fs: int,
                     start: Optional[Frames] = None,
                     end: Optional[Frames] = None):
    root.set_sampler(RootSampler(fs))
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
