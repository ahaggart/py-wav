import numpy as np
import simpleaudio as sa

from sources.Source import Source


def play_from_source(root: Source, fs: int):
    buffer = root.get_buffer(fs)

    # Ensure that highest value is in 16-bit range
    audio = buffer * (2**15 - 1) / np.max(np.abs(buffer))

    # Convert to 16-bit data
    audio = audio.astype(np.int16)

    # Start playback
    play_obj = sa.play_buffer(audio, 1, 2, fs)

    # Wait for playback to finish before exiting
    play_obj.wait_done()