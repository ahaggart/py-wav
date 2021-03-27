import time

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

from Signal import Signal
from SignalContext import SignalContext
from custom_types import Frames, Hz
from signals.BandPassSignal import BandPassSignal
from signals.WavSignal import WavSignal


def draw_fft(fft, fs, ax, title="FFT"):
    normalized = np.abs(fft) / fs
    half_sample = int(len(fft) / 2)
    fft_y = np.concatenate([normalized[half_sample:], normalized[:half_sample]])
    fft_x = np.arange(-half_sample, half_sample, step=1) * (float(fs) / len(fft))
    ax.plot(fft_x, fft_y)
    ax.set_xlabel("Hz")
    ax.title.set_text(title)


def analyze(fs: Hz, child: Signal, flt: BandPassSignal, start: Frames, end: Frames):
    fig, (ax) = plt.subplots(2, 3)

    t = np.arange(start, end, 1)
    xt = child.get_temporal(fs, start, end)
    time_plot = ax[0][0]
    time_plot.plot(t, xt)
    time_plot.title.set_text("x[t]")

    freq_plot = ax[1][0]
    xw = np.fft.fft(xt)
    draw_fft(xw, fs, freq_plot, "X[w]")

    yt = flt.get_temporal(fs, start, end)
    yt_plot = ax[0][2]
    yt_plot.plot(t, yt)
    yw = np.fft.fft(yt)
    yw_plot = ax[1][2]
    draw_fft(yw, fs, yw_plot, "Y[w]")

    ht = flt.ht_cache[fs]
    ht_plot = ax[0][1]
    ht_plot.plot(np.arange(0, len(ht), step=1) / fs, ht)
    ht_plot.title.set_text("h[t]")
    ht_plot.set_xlabel("t")

    om = np.linspace(-fs/2.0, fs/2.0, 512)
    hw_plot = ax[1][1]
    signal.freqz(
        b=ht,
        worN=om,
        plot=lambda w, h: hw_plot.plot(w, np.log10(np.abs(h))*20),
        fs=fs,
    )
    hw_plot.title.set_text("H[w] (dB)")
    hw_plot.set_xlabel("Hz")

    plt.show()

def main():
    fs = 44100
    lower = 20
    upper = 37
    num_taps = 201

    wav = WavSignal(SignalContext({
        "uuid": "wav",
        "type": "wav",
        "file": "resources/wav/please_turn_off_the_air.wav",
    }))

    flt = BandPassSignal(SignalContext.with_refs({
        "uuid": f"bp-{lower}-{upper}",
        "type": "bp",
        "band_start": lower,
        "band_stop": upper,
        "window": "hanning",
        "num_taps": num_taps,
    }, {"child": wav}))

    analyze(fs, wav, flt, 0, len(wav.get_source_buffer()))


if __name__ == "__main__":
    main()
