from __future__ import annotations

import multiprocessing
import time
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing.queues import Queue
from typing import Optional, List

import matplotlib.pyplot as plt
import numpy as np

from SignalContext import SignalContext
from custom_types import Frames, Hz
from py_wav.io.streaming import PyAudioStreaming, ChunkMetadata, StreamChunk
from signals.BandPassSignal import BandPassSignal
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
NUM_TAPS = 801

MAX_TIME_SECONDS = 20

RUN_TYPE = "play"

cutoffs = np.geomspace(MIN_FREQ, MAX_FREQ, NUM_BANDS+1)
bands = list(zip(cutoffs[:-1], cutoffs[1:]))

wav = WavSignal(SignalContext({
    "uuid": "wav",
    "type": "wav",
    "file": "resources/wav/please_turn_off_the_air.wav",
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

base_signal = stream_amp

LENGTH = Frames(len(wav.get_source_buffer()))

extracted_bands = []
envelopes = []
components = []
for lower, upper in bands:
    bp = BandPassSignal(SignalContext.with_refs({
        "uuid": f"bp-{lower}-{upper}",
        "type": "bp",
        "band_start": lower,
        "band_stop": upper,
        "window": "hanning",
        "num_taps": NUM_TAPS,
    }, {"child": base_signal}))

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
        "freq": lower,
        "dur": MAX_TIME_SECONDS,
    }))

    component = ScaledSignal(SignalContext.with_refs({
        "uuid": f"component-{lower}-{upper}",
        "type": "scaled",
    }, {"child": carrier, "factor": env}))

    components.append(component)

component_sum = SummingSignal(SignalContext.with_refs({
    "uuid": "bp_sum",
    "type": "sum"
}, {"children": components}))


if RUN_TYPE == "draw":
    fig, (axes) = plt.subplots(2+len(components), 1)
    wav_out = wav.get_temporal(FS, 0, LENGTH)
    bp_out = component_sum.get_temporal(FS, 0, LENGTH)
    axes[0].plot(wav_out)
    for i in range(len(components)):
        axes[i+1].plot(components[i].get_temporal(FS, 0, LENGTH))
        axes[i+1].plot(envelopes[i].get_temporal(FS, 0, LENGTH))
        print(extracted_bands[i].band_start)
    axes[len(components)+1].plot(bp_out, color='green')
    plt.show()
    exit()
elif RUN_TYPE == "analyze":
    fig, (axes) = plt.subplots(2, 3)
    exit()

WIDTH = 4
CHANNELS = 1
FRAMES_PER_BUFFER = 256

in_queue = multiprocessing.Queue(maxsize=3)
out_queue = multiprocessing.Queue()
meta_queue = multiprocessing.Queue()


def process_data(input_queue: Queue[Optional[StreamChunk]],
                 output_queue: Queue[Optional[StreamChunk]]):
    print("starting worker thread")
    total_frames = 0
    for chunk in iter(input_queue.get, None):
        metadata = chunk.metadata
        stream_signal.put_data(metadata.start, metadata.end, chunk.buf)
        with metadata.processing_time:
            out = component_sum.get_temporal(FS, metadata.start, metadata.end)
        output_queue.put(StreamChunk(out, metadata))
        total_frames = metadata.end
    output_queue.put(None)
    print("shutting down worker thread")
    return total_frames


def input_loop(chunk_size: Frames,
               input_queue: Queue[Optional[StreamChunk]]):
    cur_frame = 0
    try:
        while True:
            if not input_queue.full():
                metadata = ChunkMetadata(cur_frame, cur_frame+chunk_size)
                chunk = StreamChunk(
                    buf=wav.get_temporal(FS, metadata.start, metadata.end),
                    metadata=metadata,
                )
                input_queue.put(chunk)
                cur_frame += chunk_size
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("shutting down main thread")
        input_queue.put(None)
    return cur_frame


io_helper = PyAudioStreaming(FS, CHANNELS, FRAMES_PER_BUFFER)
io_daemon = io_helper.start_daemon(in_queue, out_queue, meta_queue)
io_daemon.start()

metadata: List[ChunkMetadata] = []

with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(process_data, in_queue, out_queue)
    try:
        while True:
            chunk_metadata: ChunkMetadata = meta_queue.get()
            metadata.append(chunk_metadata)
            if chunk_metadata.end > MAX_TIME_SECONDS * FS:
                print(f"Reach max time: {MAX_TIME_SECONDS} seconds")
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("initiating shutdown")
        with io_helper.running.get_lock():
            io_helper.running.value = 0
    total_frames = future.result()

metadata.extend(iter(meta_queue.get, None))

input_times = [m.input_time.time for m in metadata]
processing_times = [m.processing_time.time for m in metadata]
output_times = [m.output_time.time for m in metadata]
round_trip_times = [m.round_trip_time.time for m in metadata]

print(f"frames processed: {total_frames}")
print(f"streamed length: {stream_signal.dur}")

fig, (axes) = plt.subplots(4, 1)
axes[0].plot(stream_signal.get_temporal(FS, 0, total_frames))
axes[1].plot(stream_amp.get_temporal(FS, 0, total_frames))
axes[2].plot(component_sum.get_temporal(FS, 0, total_frames))
axes[3].plot(processing_times, color='blue')
axes[3].plot(input_times, color='orange')
axes[3].plot(output_times, color='green')
axes[3].plot(round_trip_times, color='pink')
axes[3].hlines(
    y=FRAMES_PER_BUFFER/FS*1000000000,
    xmin=0,
    xmax=len(processing_times),
    color='red',
)

plt.show()
