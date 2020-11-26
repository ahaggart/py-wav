import wave

import numpy as np

import simpleaudio as sa

import matplotlib.pyplot as plt

with wave.open("resources/wav/please_turn_off_the_air.wav", "rb") as wav:
    n_frames = wav.getnframes()
    raw = wav.readframes(n_frames)
    fs = wav.getframerate()
    buffer = np.frombuffer(raw, dtype=np.int32)

# Ensure that highest value is in 16-bit range
audio = buffer / np.max(np.abs(buffer)) * (2**15 - 1)

# Convert to 16-bit data
audio = audio.astype(np.int16)

print(fs)

plt.plot(audio)
plt.show()

# Start playback
# play_obj = sa.play_buffer(audio, 1, 2, fs)

# Wait for playback to finish before exiting
# play_obj.wait_done()
