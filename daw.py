#!/usr/bin/env python
import numpy as np
import simpleaudio as sa

from parser import SourceParser
from sources.Source import Source
from sources.registry import get_registry

fs = 44100  # 44100 samples per second


def play(root: Source, fs: int):
    buffer = root.get_buffer(fs)

    # Ensure that highest value is in 16-bit range
    audio = buffer * (2**15 - 1) / np.max(np.abs(buffer))
    
    # Convert to 16-bit data
    audio = audio.astype(np.int16)

    # Start playback
    play_obj = sa.play_buffer(audio, 1, 2, fs)

    # Wait for playback to finish before exiting
    play_obj.wait_done()


parser = SourceParser(get_registry())
root = parser.parse("resources/song.json")

play(root, fs)
