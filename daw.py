#!/usr/bin/env python
import json
import numpy as np
import matplotlib.pyplot as plt
import typing
from typing import List, Dict, Tuple

import simpleaudio as sa

from parser import construct, registered_classes
from sources.Source import Source
from sources.registry import registered_sources

fs = 44100  # 44100 samples per second

registered_classes.update(registered_sources)

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

with open("song.json") as song:
    raw = json.load(song)
    root = construct(raw)

play(root, fs)