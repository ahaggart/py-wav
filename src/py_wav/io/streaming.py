from __future__ import annotations

import signal
import time
import uuid
from multiprocessing import Queue, Value, Process
from threading import Thread
from typing import Generator, Optional, TypeVar, Generic

from custom_types import Frames


class MetadataTimer:
    def __init__(self):
        self.time = None
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time_ns()

    def stop(self):
        self.end_time = time.time_ns()
        self.time = self.end_time - self.start_time

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class ChunkMetadata:
    def __init__(self, fs: Frames, start: Frames, end: Frames):
        self.id = uuid.uuid4()
        self.fs = fs
        self.start = start
        self.end = end
        self.processing_time = MetadataTimer()
        self.input_time = MetadataTimer()
        self.output_time = MetadataTimer()
        self.round_trip_time = MetadataTimer()
        self.input_wait = MetadataTimer()
        self.output_wait = MetadataTimer()


class StreamChunk:
    def __init__(self, buf, metadata: ChunkMetadata):
        self.buf = buf
        self.metadata = metadata


T = TypeVar("T")


class ChunkStream(Generic[T]):
    def __init__(self, max_depth=0):
        self.queue: Queue[Optional[T]] = Queue(maxsize=max_depth)

    def __iter__(self) -> Generator[T]:
        for chunk in iter(self.get, None):
            yield chunk

    def get(self, block=True, timeout=None):
        return self.queue.get(block=block, timeout=timeout)

    def put(self, chunk: Optional[T], block=True, timeout=None):
        self.queue.put(chunk, block=block, timeout=timeout)

    def close(self):
        self.put(None)


class AudioChunkStream(ChunkStream[StreamChunk]):
    pass


class MetadataChunkStream(ChunkStream[ChunkMetadata]):
    pass


class ChunkIO(Generic[T]):
    def __init__(self, name: str):
        self.name = name
        self.running = Value('i', 0)

    def start(self,
              in_queue: Optional[AudioChunkStream],
              out_queue: Optional[AudioChunkStream],
              metadata_queue: Optional[MetadataChunkStream]):
        with self.running.get_lock():
            self.running.value = 1
        do_output = out_queue is not None
        do_input = in_queue is not None

        with self.streaming_context(do_input, do_output) as ctx:
            out_thread = None
            in_thread = None
            if do_output:
                out_thread = Thread(
                    target=self.write_output,
                    args=(ctx, out_queue, metadata_queue),
                )
                out_thread.start()

            if do_input:
                in_thread = Thread(
                    target=self.read_input,
                    args=(ctx, in_queue),
                )
                in_thread.start()

            if out_thread is not None:
                out_thread.join()
            if in_thread is not None:
                in_thread.join()

    def start_daemon(self,
                     in_queue: Optional[AudioChunkStream],
                     out_queue: Optional[AudioChunkStream],
                     metadata_queue: Optional[MetadataChunkStream]):
        def target(iq, oq, mq):
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self.start(iq, oq, mq)

        return Process(
            name=self.name,
            target=target,
            args=(in_queue, out_queue, metadata_queue),
        )

    def is_running(self):
        with self.running.get_lock():
            return self.running.value == 1

    def stop(self):
        with self.running.get_lock():
            self.running.value = 0

    def streaming_context(self,
                          do_input: bool,
                          do_output: bool
                          ) -> T:
        raise NotImplementedError

    def read_input(self,
                   ctx: T,
                   in_queue: AudioChunkStream):
        raise NotImplementedError

    def write_output(self,
                     ctx: T,
                     out_queue: AudioChunkStream,
                     metadata_queue: MetadataChunkStream):
        raise NotImplementedError


class StreamWorker:
    def __init__(self,
                 input_stream: AudioChunkStream,
                 output_stream: AudioChunkStream):
        self.input_stream = input_stream
        self.output_stream = output_stream

    def work(self):
        print("starting worker thread")
        total_frames = 0
        for chunk in self.input_stream:
            metadata = chunk.metadata
            metadata.input_wait.stop()
            with metadata.processing_time:
                out = self.process(chunk)
            metadata.output_wait.start()
            self.output_stream.put(StreamChunk(out, metadata))
            total_frames = metadata.end
        self.output_stream.close()
        print("shutting down worker thread")
        return total_frames

    def process(self, chunk: StreamChunk):
        raise NotImplementedError
