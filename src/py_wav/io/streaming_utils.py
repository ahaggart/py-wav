from typing import List, Union

import numpy as np

from Signal import Signal
from custom_types import Frames

from py_wav.io.streaming import ChunkMetadata, AudioChunkStream, StreamChunk


def print_stats(name: str, data):
    a = np.array(data)
    print(
        f"{name}: "
        f"min={np.min(a)} "
        f"avg={np.average(a)} "
        f"med={np.median(a)} "
        f"max={np.max(a)} "
    )


def plot_timing_data(ax,
                     fs: Frames,
                     chunk_metadata: List[ChunkMetadata],
                     lines: Union[int, List[int]]):
    audio_in_times = [m.audio_in.time for m in chunk_metadata]
    input_send_times = [m.input_send.time for m in chunk_metadata]
    processor_recv_times = [m.processor_recv.time for m in chunk_metadata]
    processing_times = [m.processing_time.time for m in chunk_metadata]
    processor_send_times = [m.processor_send.time for m in chunk_metadata]
    output_recv_times = [m.output_recv.time for m in chunk_metadata]
    audio_out_times = [m.audio_out.time for m in chunk_metadata]
    round_trip_times = [m.round_trip_time.time for m in chunk_metadata]

    print_stats("audio_in_times", audio_in_times)
    print_stats("input_send_times", input_send_times)
    print_stats("processor_recv_times", processor_recv_times)
    print_stats("processing_times", processing_times)
    print_stats("processor_send_times", processor_send_times)
    print_stats("output_recv_times", output_recv_times)
    print_stats("audio_out_times", audio_out_times)
    print_stats("round_trip_times", round_trip_times)

    ns = np.arange(0, len(chunk_metadata), 1) * 1000000000 / float(fs)
    ax.plot(ns, audio_in_times, label='audio_in')
    ax.plot(ns, input_send_times, label='input_send')
    ax.plot(ns, processor_recv_times, label='processor_recv')
    ax.plot(ns, processing_times, label='processing')
    ax.plot(ns, processor_send_times, label='processor_send')
    ax.plot(ns, output_recv_times, label='output_recv')
    ax.plot(ns, audio_out_times, label='audio_out')
    ax.plot(ns, round_trip_times, label='round_trip')
    ax.legend()
    ax.hlines(
        y=lines,
        xmin=0,
        xmax=len(chunk_metadata) * 1000000000 / float(fs),
        color='red',
    )


def input_from_signal(fs: Frames,
                      signal: Signal,
                      chunk_size: Frames,
                      input_queue: AudioChunkStream) -> Frames:
    print("starting input loop")
    cur_frame = 0
    try:
        while True:
            metadata = ChunkMetadata(fs, cur_frame, cur_frame+chunk_size)
            chunk = StreamChunk(
                buf=signal.get_temporal(fs, metadata.start, metadata.end),
                metadata=metadata,
            )
            input_queue.put(chunk)
            cur_frame += chunk_size
    except KeyboardInterrupt:
        print("shutting down input loop")
        input_queue.close()
    return cur_frame
