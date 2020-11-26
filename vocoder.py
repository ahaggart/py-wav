from collections import deque

import numpy as np

from output import play_from_source
from parameters.BandPassParameter import BandPassParameter
from parameters.EnvelopeFollowingParameter import EnvelopeFollowingParameter
from parameters.FourierParameter import FourierParameter, FourierInverseParameter
from parameters.SourceParameter import SourceParameter
from sources.BufferSource import BufferSource
from sources.WavSource import WavSource

import matplotlib.pyplot as plt

from sources.waveforms.SawSource import SawSource
from sources.waveforms.SineSource import SineSource

wav_source = WavSource("resources/wav/please_turn_off_the_air.wav")

wav_source.load_source()

fs = wav_source.source_fs
dur = wav_source.get_duration(fs)

sine_source = SineSource(440, float(dur) / fs)

base_source = wav_source

fourier = FourierParameter(SourceParameter(base_source))

inverse_fourier = FourierInverseParameter(fourier)

# human hearing: 20hz - 20khz
bands = np.geomspace(20, 10000, 10)

out = np.zeros(dur)

fig, (ax) = plt.subplots(len(bands)-1+3, 1)

ax[0].plot(base_source.get_buffer(fs, 0, dur))
ax[1].plot(np.real(fourier.sample(fs, 0, dur)))

for i in range(0, len(bands)-1):
    lower = bands[i]
    upper = bands[i+1]
    band = BandPassParameter(lower, upper, fourier)
    inv = FourierInverseParameter(band)
    env = EnvelopeFollowingParameter(lower-1, inv)
    carrier = SawSource((lower + upper) / 2, dur / fs)
    # ax[i+2].plot(np.real(inv.sample(fs, 0, dur)))
    buf = carrier.get_buffer(fs, 0, dur) * env.sample(fs, 0, dur)
    out += buf
    ax[i+2].plot(buf)
    ax[i+2].plot(np.real(env.sample(fs, 0, dur)))

ax[-1].plot(out)

plt.show()

final_source = BufferSource(out, fs)

play_from_source(final_source, fs)
