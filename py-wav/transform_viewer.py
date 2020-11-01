import numpy as np

from sources.aggregations.AdditiveSource import AdditiveSource
from sources.waveforms.SineSource import SineSource
import matplotlib.pyplot as plt

from transforms.FourierTransform import FourierTransform
from transforms.filters.HarmonicFilter import HarmonicFilter

fs = 44100
freq = 440
seconds = 2

source = AdditiveSource(
    children=[
        (0, SineSource(freq, seconds)),
        (0, SineSource(freq*3, seconds)),
    ],
)
filter = HarmonicFilter([3])
transform = FourierTransform([filter])

per = int(float(fs) / freq)
dur = source.get_duration(fs)

fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2)

buffer = source.get_buffer(fs, 0, dur)
ax0.plot(buffer[:per])

fft = transform.get_dft(fs, buffer)
ax2.plot(np.abs(fft))

filtered = filter.apply(fft)
ax3.plot(np.abs(filtered))

ax1.plot(transform.apply(fs, buffer))

plt.show()
