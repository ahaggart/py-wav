from __future__ import annotations

import logging
import math
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from SignalContext import SignalContext
from custom_types import Frames, Hz
from output import play_from_buffer
from py_wav.io.signal_io import SignalStreamWorker, SignalInputManager
from py_wav.io.pyaudio import PyAudioStreaming
from py_wav.io.streaming import ChunkMetadata, AudioChunkStream, MetadataChunkStream, ChunkIO
from py_wav.io.streaming_utils import plot_timing_data
from signals.OffsetSignal import OffsetSignal
from signals.fir.BandPassSignal import BandPassSignal
from signals.ConstantSignal import ConstantSignal
from signals.ScaledSignal import ScaledSignal
from signals.SineSignal import SineSignal
from signals.StreamingSignal import StreamingSignal
from signals.SummingSignal import SummingSignal
from signals.WavSignal import WavSignal
from signals.WindowMaxSignal import WindowMaxSignal

# human hearing: 20hz - 20khz

FS = Hz(44100)
MIN_FREQ = 20
MAX_FREQ = 10000
NUM_BANDS = 10
NUM_TAPS = 101
WIDTH = 4
CHANNELS = 1
FRAMES_PER_BUFFER = 256
NS_PER_BUFFER = FRAMES_PER_BUFFER / FS * 1000000000
MAX_TIME_SECONDS = 20

RUN_TYPE = "draw_single"
# RUN_TYPE = "play_online"

# logging.basicConfig(level=logging.DEBUG, filename='out/vocoder_2.log', filemode='w')

cutoffs = np.geomspace(MIN_FREQ, MAX_FREQ, NUM_BANDS+1)
bands = list(zip(cutoffs[:-1], cutoffs[1:]))

wav = WavSignal(SignalContext({
    "uuid": "wav",
    "type": "wav",
    "file": "resources/wav/please_turn_on_the_air.wav",
}))

stream_signal = StreamingSignal(SignalContext({
    "uuid": "stream",
    "type": "stream",
    "source_fs": FS,
}))

stream_gain = ConstantSignal(SignalContext({
    "uuid": "stream-gain",
    "type": "constant",
    "value": 10,
    "dur": MAX_TIME_SECONDS,
}))

stream_amp = ScaledSignal(SignalContext.with_refs({
    "uuid": "stream-amp",
    "type": "scaled",
}, {"child": stream_signal, "factor": stream_gain}))

base_signal = stream_signal

LENGTH = Frames(len(wav.get_source_buffer()))

extracted_bands = []
envelopes = []
components = []
for lower, upper in bands:
    fs_opts = [441, 882, 1764, 8820]
    bp_fs = 44100
    for fs_opt in fs_opts:
        if upper * 3 < fs_opt:
            bp_fs = fs_opt
            break
    print(f"using {bp_fs} for band {lower}:{upper}")
    # bp_fs = 44100
    # if bp_fs == 4410:
    #     offset_s = math.ceil((NUM_TAPS-1)/2) / 44100
    # else:
    #     offset_s = math.ceil((NUM_TAPS-1)/2) / 4410

    bp = BandPassSignal(SignalContext.with_refs({
        "uuid": f"bp-{lower}-{upper}",
        "type": "bp",
        "band_start": lower,
        "band_stop": upper,
        "window": "hanning",
        "num_taps": NUM_TAPS,
        "fs": bp_fs,
    }, {"child": base_signal}))

    # offset = OffsetSignal(SignalContext.with_refs({
    #     "uuid": f"offset-{lower}-{upper}",
    #     "type": "offset",
    #     "offset": offset_s,
    # }, {"child": bp}))

    extracted_bands.append(bp)

    env = WindowMaxSignal(SignalContext.with_refs({
        "uuid": f"env-{lower}-{upper}",
        "type": "win_max",
        "length": 1 / (1*upper),
    }, {"child": bp}))

    envelopes.append(env)

    carrier = SineSignal(SignalContext({
        "uuid": f"carrier-{lower}",
        "type": "sine",
        "freq": math.sqrt(lower*lower+upper*upper),
        "dur": MAX_TIME_SECONDS,
    }))

    component = ScaledSignal(SignalContext.with_refs({
        "uuid": f"component-{lower}-{upper}",
        "type": "scaled",
    }, {"child": carrier, "factor": env}))

    components.append(component)

component_sum = SummingSignal(SignalContext.with_refs({
    "uuid": "bp_sum",
    "type": "sum",
}, {"children": components}))


def plot_with_freq(ax, buf, fs: Hz, lower: Hz, upper: Hz, freq_limit: Hz, label: str = None, marker=None):
    ax[0].get_xaxis().set_visible(False)
    ax[1].get_xaxis().set_visible(False)
    ax[0].plot(buf, label=label, marker=marker)
    fft = np.fft.fft(buf)
    if freq_limit is not None:
        freq_limit = min(freq_limit, fs/2)
    else:
        freq_limit = fs/2
    idx_limit = math.floor(freq_limit * len(fft) / fs)
    fft_centered = np.abs(fft[:idx_limit])
    freq_space = np.linspace(0, freq_limit, idx_limit)
    ax[1].plot(freq_space, fft_centered, label=label)
    ax[1].vlines(
        x=[lower, upper],
        ymin=np.min(fft_centered),
        ymax=np.max(fft_centered),
        color='red',
    )


if RUN_TYPE == "draw":
    fig, (axes) = plt.subplots(2+len(components), 2)
    stream_signal.put_data(0, LENGTH, wav.get_temporal(FS, 0, LENGTH))
    wav_out = stream_amp.get_temporal(FS, LENGTH, LENGTH)
    bp_out = component_sum.get_temporal(FS, LENGTH, LENGTH)
    axes[0][0].plot(wav_out)
    for i in range(len(extracted_bands)):
        component = extracted_bands[i]
        buf = np.zeros(LENGTH)
        chunk_size = 512
        for step in range(0, math.ceil(LENGTH/chunk_size)):
            end = min((step+1)*chunk_size, LENGTH)
            buf[end-chunk_size:end] = component.get_temporal(FS, chunk_size, end)
        plot_with_freq(
            axes[i+1],
            buf=buf,
            fs=FS,
            lower=component.band_start,
            upper=component.band_stop,
            freq_limit=component.band_stop*2,
        )
        axes[i+1][0].plot(component.get_temporal(FS, LENGTH, LENGTH)-buf)
        # axes[i+1][0].plot(components[i].get_temporal(FS, LENGTH, LENGTH))
        # axes[i+1][0].plot(envelopes[i].get_temporal(FS, LENGTH, LENGTH))
        # print(extracted_bands[i].band_start)
    axes[len(components)+1][0].plot(bp_out, color='green')
    plt.show()
    exit()
elif RUN_TYPE == "draw_single":
    stream_signal.put_data(0, LENGTH, wav.get_temporal(FS, 0, LENGTH))
    stream_signal.put_data(LENGTH, LENGTH+10000, np.zeros(10000))
    fig, (axes) = plt.subplots(1, 2)
    component = extracted_bands[0]
    chunk_size = 200
    one_shot = component.get_temporal(FS, 0, LENGTH)
    buf = np.zeros(LENGTH)
    for end in range(LENGTH, 0, -chunk_size):
        sample_size = min(end, chunk_size)
        start = end - sample_size
        buf[start:end] = component.get_temporal(FS, start, end)

    offset = 60073
    sample_end = LENGTH - offset
    sample_start = sample_end-chunk_size
    single_chunk = component.get_temporal(FS, sample_start, sample_end)
    one_shot_chunk = one_shot[sample_start:sample_end]

    plot_with_freq(
        axes,
        buf=single_chunk,
        fs=FS,
        lower=component.band_start,
        upper=component.band_stop,
        freq_limit=None,
        # freq_limit=component.band_stop*2,
        label="chunked",
    )
    plot_with_freq(
        axes,
        buf=one_shot_chunk,
        fs=FS,
        lower=component.band_start,
        upper=component.band_stop,
        freq_limit=None,
        # freq_limit=component.band_stop*2,
        label="one-shot",
    )
    axes[0].plot(one_shot_chunk-single_chunk, label="diff")
    axes[0].legend()
    axes[1].legend()
    plt.show()
    # axes[i+1][0].plot(components[i].get_temporal(FS, LENGTH, LENGTH))
    # axes[i+1][0].plot(envelopes[i].get_temporal(FS, LENGTH, LENGTH))
    # print(extracted_bands[i].band_start)
    exit()
elif RUN_TYPE == "analyze":
    fig, (axes) = plt.subplots(2, 3)
    exit()
elif RUN_TYPE == "play_online":
    pass
elif RUN_TYPE == "play_offline":
    stream_signal.put_data(0, LENGTH, wav.get_temporal(FS, 0, LENGTH))
    buf = component_sum.get_temporal(FS, 0, LENGTH)
    play_from_buffer(FS, buf)
    exit()
else:
    print("Please select an option")
    exit()

in_queue = AudioChunkStream(max_depth=2)
out_queue = AudioChunkStream(max_depth=2)
meta_queue = MetadataChunkStream()
pyaudio_io = PyAudioStreaming(FS, CHANNELS, FRAMES_PER_BUFFER)
signal_input = SignalInputManager(wav)  # use this one to play a wav file
io_orchestrator = ChunkIO(FS, FRAMES_PER_BUFFER, signal_input, pyaudio_io)
io_daemon = io_orchestrator.start_daemon(in_queue, out_queue, meta_queue)

metadata: List[ChunkMetadata] = []

worker = SignalStreamWorker(in_queue, stream_signal, component_sum, out_queue)

with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(worker.work)
    try:
        while True:
            chunk_metadata: ChunkMetadata = meta_queue.get()
            metadata.append(chunk_metadata)
            if chunk_metadata is None:
                print(f"ChunkStream processing aborted!")
                break
            if chunk_metadata.end > MAX_TIME_SECONDS * FS:
                print(f"Reach max time: {MAX_TIME_SECONDS} seconds")
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("initiating shutdown")
        io_orchestrator.stop()
    total_frames = future.result()

metadata.extend(meta_queue)

print(f"frames processed: {total_frames}")
print(f"streamed length: {stream_signal.dur}")

fig, (axes) = plt.subplots(2, 1)
axes[0].plot(component_sum.get_temporal(FS, 0, total_frames))
plot_timing_data(axes[1], FS, metadata, lines=NS_PER_BUFFER)
plt.show()
