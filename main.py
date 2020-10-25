#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt

import simpleaudio as sa

import Note

frequency = 440  # Our played note will be 440 Hz
fs = 44100  # 44100 samples per second
seconds = 3  # Note duration of 3 seconds

# Generate array with seconds*sample_rate steps, ranging between 0 and seconds
t = np.linspace(0, seconds, seconds * fs, False)

# Generate a 440 Hz sine wave
note = np.sin(frequency * t * 2 * np.pi)

per = int((1.0/frequency) * fs)

saw = np.array([i % per for i in range(0, seconds * fs) ])
sqr = np.array([-(per/2) if i % per > per / 2 else (per/2) for i in range(0, seconds * fs) ])

def play(note):
    # Ensure that highest value is in 16-bit range
    audio = note * (2**15 - 1) / np.max(np.abs(note))
    # Convert to 16-bit data
    audio = audio.astype(np.int16)

    # Start playback
    play_obj = sa.play_buffer(audio, 1, 2, fs)

    # Wait for playback to finish before exiting
    play_obj.wait_done()

# play(note)
# fft = np.abs(np.fft.fft(saw, fs)) / fs
# half_sample = int(fs/2)
# fft_y = np.concatenate([fft[half_sample:],fft[:half_sample]])
# fft_x = [i for i in range(-half_sample,half_sample)]
# plt.plot(fft_x, fft_y)
# plt.show()
play(np.array(list(Note.PureNote(frequency, fs).record(3))))
# play(saw)
# play(sqr)
# play(saw + sqr)
