from __future__ import annotations

import multiprocessing
import signal
import threading
import time
import uuid
from multiprocessing.queues import Queue
from typing import Optional, NewType

import pyaudio

import numpy as np
from pyaudio import Stream

from custom_types import Frames, Hz


class MetadataTimer:
    def __init__(self):
        self.time = None
        self.start = None
        self.end = None

    def start_timer(self):
        self.start = time.time_ns()

    def stop_timer(self):
        self.end = time.time_ns()
        self.time = self.end - self.start

    def __enter__(self):
        self.start_timer()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_timer()


class ChunkMetadata:
    def __init__(self, start: Frames, end: Frames):
        self.id = uuid.uuid4()
        self.start = start
        self.end = end
        self.processing_time = MetadataTimer()
        self.input_time = MetadataTimer()
        self.output_time = MetadataTimer()
        self.round_trip_time = MetadataTimer()


class StreamChunk:
    def __init__(self, buf, metadata: ChunkMetadata):
        self.buf = buf
        self.metadata = metadata


class PyAudioStreaming:
    def __init__(self, fs: Hz, channels: int, chunk_size: Frames):
        self.chunk_size = chunk_size
        self.fs = int(fs)
        self.channels = int(channels)
        self.running = multiprocessing.Value('i', 0)

    def read_input(self,
                   audio_in: Stream,
                   buffer_out: Queue[Optional[StreamChunk]]):
        print("starting input")
        cur_frame = 0
        while self.running.value == 1:
            metadata = ChunkMetadata(
                start=cur_frame,
                end=cur_frame + self.chunk_size,
            )

            in_data = audio_in.read(self.chunk_size)
            with metadata.input_time:
                buf = np.frombuffer(in_data, dtype=np.float32)

            chunk = StreamChunk(buf, metadata=metadata)
            metadata.round_trip_time.start_timer()
            buffer_out.put(chunk)
            cur_frame += self.chunk_size
        buffer_out.put(None)
        print("finished input")

    def write_output(self,
                     buffer_in: Queue[Optional[StreamChunk]],
                     audio_out: Stream,
                     metadata_out: Queue[Optional[ChunkMetadata]]):
        print("starting output")
        for chunk in iter(buffer_in.get, None):
            chunk.metadata.round_trip_time.stop_timer()
            with chunk.metadata.output_time:
                frames = chunk.buf.astype(np.float32).tobytes()
                audio_out.write(frames, num_frames=len(chunk.buf))
            if metadata_out is not None:
                metadata_out.put(chunk.metadata)
        if metadata_out is not None:
            metadata_out.put(None)
        print("finished output")

    def start(self,
              in_queue: Optional[Queue],
              out_queue: Optional[Queue],
              metadata_queue: Optional[Queue]):
        with self.running.get_lock():
            self.running.value = 1
        p = pyaudio.PyAudio()
        do_output = out_queue is not None
        do_input = in_queue is not None
        stream = p.open(format=pyaudio.paFloat32,
                        channels=self.channels,
                        rate=self.fs,
                        input=do_input,
                        output=do_output,
                        frames_per_buffer=self.chunk_size)
        stream.start_stream()

        try:
            out_thread = None
            in_thread = None
            if do_output:
                out_thread = threading.Thread(
                    target=self.write_output,
                    args=(out_queue, stream, metadata_queue),
                )
                out_thread.start()

            if do_input:
                in_thread = threading.Thread(
                    target=self.read_input,
                    args=(stream, in_queue),
                )
                in_thread.start()

            if out_thread is not None:
                out_thread.join()
            if in_thread is not None:
                in_thread.join()
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def start_daemon(self,
                     in_queue: Optional[Queue],
                     out_queue: Optional[Queue],
                     metadata_queue: Optional[Queue]):
        def target(iq, oq, mq):
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self.start(iq, oq, mq)

        return multiprocessing.Process(
            name="pyaudio",
            target=target,
            args=(in_queue, out_queue, metadata_queue),
        )





