import math
import time
from typing import Dict

import numpy as np
from scipy import signal, fft


def one_shot_convolution(xt, ht):
    return np.convolve(xt, ht, mode='valid')


def overlap_save_convolution(xt, ht):
    _M = len(ht)
    overlap = _M - 1
    _N = fft.next_fast_len(8 * overlap)
    step_size = _N - overlap
    _H = np.fft.rfft(ht, _N)
    pos = 0

    yt = np.zeros(len(xt))

    while pos + _N <= len(xt):
        yt_k = np.fft.irfft(np.fft.rfft(xt[pos:pos+_N]) * _H)
        yt[pos:pos+step_size] = np.real(yt_k[_M-1:_N])
        pos += step_size

    return yt, pos


def benchmark(chunksize, xt, ht):
    chunks = np.array_split(xt, len(xt)/chunksize)
    start = time.time_ns()
    for chunk in chunks:
        np.convolve(xt, ht)
    end = time.time_ns()
    return end-start


class Timer:
    def __init__(self, name: str, profiles: Dict[str, int]):
        self.name = name
        self.profiles = profiles
        self.start = 0
        self.end = 0
        self.tot = 0

    def __enter__(self):
        self.start = time.time_ns()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time_ns()
        self.tot = self.end - self.start
        self.profiles[self.name] = self.tot

    def get_time(self):
        return self.tot


class Profiles:
    def __init__(self, params: dict = None, profiles=None):
        self.params = params if params is not None else {}
        if profiles is not None:
            self.profiles = profiles
        else:
            self.profiles = {}

    def get_profiles(self):
        return self.profiles.copy()

    def get_params(self):
        return self.params.copy()

    def profile(self, name: str):
        return Timer(name, self.profiles)

    def sub_profile(self, name: str, params: dict = None):
        self.profiles[name] = {}
        return Profiles(params, self.profiles[name])

    def __repr__(self):
        return str(self.profiles)


class IncrementalFilter:
    def __init__(self, ht, xt):
        self.ht = ht
        self.src = xt

    def get(self, start: int, end: int):
        """Compute yt at the given points.
        convolve returns N + M - 1 samples
        [0:M-1] samples have lower boundary effect
        [N:N+M-1] samples have upper boundary effect

        In order to sample start:end without boundary effects:
        1. "back-pad" N by M-1
        2. drop last M-1 points
        """
        # back-pad the sample to avoid boundary effects
        sample_start = max(0, start-len(self.ht)+1)
        sample_pad = start - sample_start
        frames = np.arange(sample_start, end, 1)
        sample = self.src[frames]
        conv = np.convolve(sample, self.ht)

        return conv[sample_pad:-len(self.ht)+1]


def profile_chunk_size(filt: IncrementalFilter,
                       chunk_size: int,
                       input_size: int,
                       profiles: Profiles,
                       prefix: str = ""):
    starts = range(0, input_size, chunk_size)
    ends = map(lambda s: min(s+chunk_size, input_size), starts)
    ranges = zip(starts, ends)
    with profiles.profile(f"{prefix}chunk_size:{chunk_size}"):
        for start, end in ranges:
            filt.get(start, end)


def main():
    fs = 44100
    n = 10
    m = 801

    t = np.linspace(0, 1, n)
    saw = signal.sawtooth(5 * t * np.pi * 2)

    lowpass = signal.firwin(
        numtaps=m,
        cutoff=2000,
        fs=fs,
        window='hanning',
        pass_zero='lowpass',
    )

    profiles = Profiles()
    alg_profiles = profiles.sub_profile("alg")

    with alg_profiles.profile("overlap-save"):
        overlap_save_result, result_size = overlap_save_convolution(saw, lowpass)

    with alg_profiles.profile("one-shot"):
        one_shot_result = one_shot_convolution(saw, lowpass)

    eq = np.allclose(
        overlap_save_result[:result_size],
        one_shot_result[:result_size]
    )

    print(f"Overlap-save == One-shot: {eq}")

    rng = np.random.default_rng()
    xt = rng.random(1000000)
    ht = rng.random(21)
    inc_filt = IncrementalFilter(ht, xt)

    iter_profiles = profiles.sub_profile("iter", {
        "input_size": len(xt),
        "filter_size": len(ht),
    })

    with iter_profiles.profile("convolve"):
        np.convolve(xt, ht)

    with iter_profiles.profile("one-shot"):
        inc_filt.get(0, len(xt))

    chunk_sizes = [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]

    for chunk_size in chunk_sizes:
        profile_chunk_size(inc_filt, chunk_size, len(xt), iter_profiles)

    print("Num Taps\tName\tTime\tSamples/s")
    for name, dur in iter_profiles.get_profiles().items():
        per_second = len(xt) / dur * 1000000000
        print(f"{m}\t{name}\t{dur}\t{per_second}")


if __name__ == "__main__":
    main()
