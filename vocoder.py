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

DRAW_COMPONENTS = False

# human hearing: 20hz - 20khz
MIN_FREQ = 20
MAX_FREQ = 10000
NUM_BANDS = 10

wav_source = WavSource("resources/wav/please_turn_on_the_air.wav")

wav_source.load_source()

fs = wav_source.source_fs
dur = wav_source.get_duration(fs)

sine_source = SineSource(440, float(dur) / fs)

base_source = wav_source

fourier = FourierParameter(SourceParameter(base_source))

inverse_fourier = FourierInverseParameter(fourier)

bands = np.geomspace(MIN_FREQ, MAX_FREQ, NUM_BANDS+1)

out = np.zeros(dur)

envelopes = []
components = []

for i in range(0, len(bands)-1):
    lower = bands[i]
    upper = bands[i+1]
    band = BandPassParameter(lower, upper, fourier)
    inv = FourierInverseParameter(band)
    env = EnvelopeFollowingParameter(lower-1, inv)
    avg_freq = (lower + upper) / 2
    fund_freq = (np.abs(np.argmax(band.sample(fs, 0, dur)) - dur / 2)) * float(fs) / dur
    carrier_freq = fund_freq
    print(f"lower: {lower} upper: {upper} avg: {avg_freq} fund: {fund_freq}")
    carrier = SineSource(carrier_freq, dur / fs)
    buf = carrier.get_buffer(fs, 0, dur) * env.sample(fs, 0, dur)
    out += buf
    envelopes.append(env)
    components.append(buf)

if DRAW_COMPONENTS:
    fig, (ax) = plt.subplots(len(bands) - 1 + 3, 1)

    ax[0].plot(base_source.get_buffer(fs, 0, dur))
    ax[1].plot(np.real(fourier.sample(fs, 0, dur)))
    ax[-1].plot(out)

    for i, buf, env in zip(range(len(components)), components, envelopes):
        ax[i + 2].plot(buf)
        ax[i + 2].plot(np.real(env.sample(fs, 0, dur)))
    plt.show()

final_source = BufferSource(out, fs)

play_from_source(final_source, fs)
