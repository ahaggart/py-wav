from typing import List, Union

import numpy as np

from Signal import Signal
from custom_types import Frames

from py_wav.io.streaming import ChunkMetadata, AudioChunkStream, StreamChunk


def plot_timing_data(ax,
                     fs: Frames,
                     chunk_metadata: List[ChunkMetadata],
                     lines: Union[int, List[int]]):
    input_times = [m.input_time.time for m in chunk_metadata]
    processing_times = [m.processing_time.time for m in chunk_metadata]
    output_times = [m.output_time.time for m in chunk_metadata]
    round_trip_times = [m.round_trip_time.time for m in chunk_metadata]
    input_wait_times = [m.input_wait.time for m in chunk_metadata]
    output_wait_times = [m.output_wait.time for m in chunk_metadata]
    get_wait_times = [m.processor_wait.time for m in chunk_metadata]

    ns = np.arange(0, len(chunk_metadata), 1) * 1000000000 / float(fs)
    ax.plot(ns, processing_times, label='processing')
    ax.plot(ns, input_times, label='read')
    ax.plot(ns, output_times, label='write')
    ax.plot(ns, round_trip_times, label='round_trip')
    ax.plot(ns, input_wait_times, label='input_queue')
    ax.plot(ns, output_wait_times, label='output_queue')
    ax.plot(ns, get_wait_times, label='processor_wait')
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
