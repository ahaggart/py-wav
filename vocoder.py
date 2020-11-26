import matplotlib.pyplot as plt
import numpy as np

from SourceState import SourceState
from output import play_from_source
from parameters.BandPassParameter import BandPassParameter
from parameters.EnvelopeFollowingParameter import EnvelopeFollowingParameter
from parameters.SourceParameter import SourceParameter
from parameters.spectral.FourierParameter import FourierParameter, FourierInverseParameter
from sources.WavSource import WavSource
from sources.aggregations.AdditiveSource import AdditiveSource
from sources.transform.ScaledSource import ScaledSource
from sources.waveforms.SineSource import SineSource

DRAW_COMPONENTS = True

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

envelopes = []
components = []

for i in range(0, len(bands)-1):
    lower = bands[i]
    upper = bands[i+1]
    band = BandPassParameter(lower, upper, fourier)
    inv = FourierInverseParameter(band)
    env = EnvelopeFollowingParameter(lower, inv)
    avg_freq = (lower + upper) / 2
    center_idx = band.get_period(fs) / 2
    fund_freq = (np.abs(np.argmax(band.get_buffer(fs)) - center_idx)) * float(fs) / dur
    carrier_freq = fund_freq
    print(f"lower: {lower} upper: {upper} avg: {avg_freq} fund: {fund_freq}")
    carrier = SineSource(carrier_freq, dur / fs)
    component = ScaledSource(env, carrier)
    envelopes.append(env)
    components.append(component)

# sum the frequency band components
out_source = AdditiveSource(list((0, c) for c in components))
out_source.set_state(SourceState())

if DRAW_COMPONENTS:
    num_pre_cmp = 1
    num_cmp = len(bands) - 1
    num_post_cmp = 1
    num_plots = num_cmp + num_pre_cmp + num_post_cmp
    fig, (ax) = plt.subplots(num_plots, 1)
    ax[0].plot(base_source.get_buffer(fs, 0, dur))
    # ax[1].plot(np.real(fourier.get_buffer(fs)))
    ax[-1].plot(out_source.sample(fs, 0, 0, dur))

    for i, cmp, env in zip(range(len(components)), components, envelopes):
        buf = cmp.sample(fs, 0, 0, dur)
        ax[i + num_pre_cmp].plot(buf)
        ax[i + num_pre_cmp].plot(np.real(env.get_buffer(fs, 0, dur)))
    plt.show()

final_source = out_source

play_from_source(final_source, fs, dur)
