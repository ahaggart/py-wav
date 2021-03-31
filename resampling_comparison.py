import math
import wave
from collections import defaultdict

import numpy as np
from scipy.signal import resample_poly, firwin
import matplotlib.pyplot as plt


def process_fir(buf, fs, num_taps, lower, upper):
    ht = firwin(
        num_taps,
        cutoff=(lower, upper),
        window='hanning',
        fs=fs,
        pass_zero='bandpass',
    )
    group_delay = math.floor((num_taps-1)/2)
    return np.convolve(buf, ht)[group_delay:group_delay+len(buf)]


def process_res(buf, fs, factor, num_taps, lower, upper):
    downsampled = resample_poly(buf, up=1, down=factor)[:len(buf)]
    processed = process_fir(downsampled, fs//factor, num_taps, lower, upper)
    return resample_poly(processed, up=factor, down=1)[:len(buf)]


def process_staged_resample(buf, fs, factors, num_taps, lower, upper):
    cur = buf
    for factor in factors:
        cur = resample_poly(cur, up=1, down=factor)[:len(buf)]
    processed = process_fir(cur, fs // np.product(factors), num_taps, lower, upper)
    cur = processed
    for factor in reversed(factors):
        cur = resample_poly(cur, up=factor, down=1)[:len(buf)]
    return cur


def plot_with_freq(ax, buf, fs, lower, upper, freq_limit):
    ax[0].get_xaxis().set_visible(False)
    ax[1].get_xaxis().set_visible(False)
    ax[0].plot(buf)
    fft = np.fft.fft(buf)
    freq_limit = min(freq_limit, fs/2)
    idx_limit = math.floor(freq_limit * len(fft) / fs)
    fft_centered = np.abs(np.concatenate([
        fft[-idx_limit:],
        fft[:idx_limit],
    ]))
    freq_space = np.linspace(-freq_limit, freq_limit, idx_limit*2)
    ax[1].plot(freq_space, fft_centered)
    ax[1].vlines(
        x=[-upper, -lower, lower, upper],
        ymin=np.min(fft_centered),
        ymax=np.max(fft_centered),
        color='red',
    )


def get_diff(a, b, window_size):
    a_smoothed = np.convolve(a, np.ones(window_size) / window_size, mode='same')
    b_smoothed = np.convolve(b, np.ones(window_size) / window_size, mode='same')
    return a_smoothed - b_smoothed


def plot_diff(ax, a, b, window_size):
    ax.plot(get_diff(a, b, window_size))


def load_wav():
    wav_file = "resources/wav/please_turn_on_the_air.wav"

    with wave.open(wav_file, 'rb') as w:
        n_frames = w.getnframes()
        fs = w.getframerate()
        raw_wav = np.frombuffer(w.readframes(n_frames), dtype=np.int32)
        base_buffer = raw_wav * 1.0 / np.max(np.abs(raw_wav))

    return fs, base_buffer


def process_fft(buf, fs, lower, upper):
    fft = np.fft.fft(buf)
    fft_lower_cutoff = math.floor(lower * len(fft) / fs)
    fft_upper_cutoff = math.floor(upper * len(fft) / fs)
    processed_fft = np.copy(fft)
    processed_fft[-fft_lower_cutoff:] = 0
    processed_fft[:fft_lower_cutoff] = 0
    processed_fft[fft_upper_cutoff:-fft_upper_cutoff] = 0
    return np.real(np.fft.ifft(processed_fft))


def plot_diffs():
    lower = 20
    upper = 37  # Hz
    fs, buf = load_wav()

    fft_processed_buffer = process_fft(buf, fs, lower, upper)

    fir_100 = process_fir(buf, fs, 100, lower, upper)
    fir_1000 = process_fir(buf, fs, 1000, lower, upper)
    fir_10000 = process_fir(buf, fs, 10000, lower, upper)

    res_441_100 = process_res(buf, fs, 100, 100, lower, upper)
    res_441_1000 = process_res(buf, fs, 100, 1000, lower, upper)
    res_147_100 = process_res(buf, fs, 300, 100, lower, upper)
    res_147_1000 = process_res(buf, fs, 300, 1000, lower, upper)

    staged_147_100 = process_staged_resample(buf, fs, [3, 10, 10], 100, lower, upper)
    staged_441_100 = process_staged_resample(buf, fs, [10, 10], 100, lower, upper)

    res_300_100 = process_res(buf, fs, 147, 100, lower, upper)

    fir_results = [
        ("fir_100", fir_100),
        ("fir_1000", fir_1000),
        ("fir_10000", fir_10000),
        ("res_441_100", res_441_100),
        ("res_441_1000", res_441_1000),
        ("res_147_100", res_147_100),
        ("res_147_1000", res_147_1000),
        # ("staged_147_100", staged_147_100),
        # ("staged_441_100", staged_441_100),
        # ("res_300_100", res_300_100),
    ]

    freq_limit = upper * 2
    fig, (ax) = plt.subplots(len(fir_results)+2, 2)
    plot_with_freq(ax[0], buf, fs, lower, upper, freq_limit)
    plot_with_freq(ax[1], fft_processed_buffer, fs, lower, upper, freq_limit)

    for (name, fir_result), ax_row in zip(fir_results, ax[2:]):
        print(f"analyzing {name}")
        ax_row[0].set_ylabel(name, rotation=0)
        plot_with_freq(ax_row, fir_result, fs, lower, upper, freq_limit)
        plot_diff(ax_row[0], fft_processed_buffer, fir_result, 10)
        avg_diff = np.average(np.abs(get_diff(fft_processed_buffer, fir_result, 10)))
        print(f"avg_diff: {avg_diff}")

    fig.tight_layout()
    plt.show()


def plot_error():
    fs = 44100
    buf = np.random.random_sample(100000)
    factors = [1, 2, 3, 5, 7, 10, 100, 147, 300]
    taps = [100]
    ends = np.linspace(1, 20000, 100)
    bands = zip(ends[:-1], ends[1:])

    diffs = defaultdict(lambda: defaultdict(list))
    for lower, upper in bands:
        fft = process_fft(buf, fs, lower, upper)
        for tap in taps:
            for factor in factors:
                if fs / 2 < upper * factor:
                    continue
                print(f"fs={fs} factor={factor} taps={tap} band={lower},{upper}")
                flt = process_res(buf, fs, factor, tap, lower, upper)
                diffs[factor][tap].append(np.average(np.abs(get_diff(fft, flt, 10))))

    fig, (axes) = plt.subplots(1, 1)
    for factor, diffs_by_tap in diffs.items():
        for tap, diff in diffs_by_tap.items():
            axes.plot(
                np.log10(ends[1:len(diff)+1]),
                diff,
                label=f'{factor}f_{tap}t',
            )
    axes.legend()
    plt.show()


def chunking_comparison():
    fs, wav = load_wav()

    cutoff = 200
    num_taps = 1001
    chunk_size = 1024
    buf = np.zeros(math.ceil(len(wav)/chunk_size)*chunk_size)
    buf[0:len(wav)] = wav

    ht = firwin(
        num_taps,
        cutoff=cutoff,
        window='hanning',
        fs=fs,
        pass_zero='highpass',
    )

    fir_oneshot = np.convolve(buf, ht)[:len(buf)]

    fir_chunked = np.zeros(len(buf))
    for start in range(0, len(buf), chunk_size):
        sample_start = max(start-(num_taps-1), 0)
        pad_amount = start - sample_start
        full_chunk = np.convolve(buf[sample_start:start+chunk_size], ht)[pad_amount:]
        fir_chunked[start:start+chunk_size] = full_chunk[:chunk_size]

    print(np.allclose(fir_oneshot, fir_chunked))

    factor = 10
    ht_dn = firwin(
        num_taps,
        cutoff=cutoff,
        window='hanning',
        fs=fs//factor,
        pass_zero='highpass',
    )

    res_chunked = np.zeros(len(buf))
    for start in range(0, len(buf), chunk_size):
        sample_start = max(start-(num_taps-1), 0)
        pad_amount = start - sample_start
        sample = buf[sample_start:start+chunk_size]
        dn = resample_poly(sample, up=1, down=factor)
        processed = np.convolve(dn, ht_dn)
        up = resample_poly(processed, up=factor, down=1)[pad_amount:]
        res_chunked[start:start+chunk_size] = up[:chunk_size]

    print(np.allclose(fir_oneshot, res_chunked))

    fig, (axes) = plt.subplots(3, 1)
    axes[0].plot(fir_oneshot)
    axes[1].plot(res_chunked)

    plt.show()


if __name__ == "__main__":
    chunking_comparison()
