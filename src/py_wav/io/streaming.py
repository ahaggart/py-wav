from __future__ import annotations

import signal
import time
import uuid
from multiprocessing import Value, Process
from threading import Thread
from typing import Optional, TypeVar, Generic

from custom_types import Frames
from py_wav.io.core import ChunkStream


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

    @classmethod
    def started(cls):
        t = MetadataTimer()
        t.start()
        return t


class ChunkMetadata:
    def __init__(self, fs: Frames, start: Frames, end: Frames):
        self.id = uuid.uuid4()
        self.fs = fs
        self.start = start
        self.end = end
        self.processing_time = MetadataTimer()
        self.audio_in = MetadataTimer()
        self.audio_out = MetadataTimer()
        self.round_trip_time = MetadataTimer()
        self.input_send = MetadataTimer()
        self.processor_recv = None
        self.processor_send = MetadataTimer()
        self.output_recv = None


class StreamChunk:
    def __init__(self, buf, metadata: ChunkMetadata):
        self.buf = buf
        self.metadata = metadata


T = TypeVar("T")


class AudioChunkStream(ChunkStream[StreamChunk]):
    pass


class MetadataChunkStream(ChunkStream[ChunkMetadata]):
    pass


class IOContext:
    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def use_for_input(self):
        raise NotImplementedError

    def use_for_output(self):
        raise NotImplementedError


class DummyContext:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def use_for_input(self):
        pass

    def use_for_output(self):
        pass


class InputManager:
    def get_context(self) -> IOContext:
        raise NotImplementedError

    def read_input(self, ctx: IOContext, metadata: ChunkMetadata):
        raise NotImplementedError


class OutputManager:
    def get_context(self) -> IOContext:
        raise NotImplementedError

    def write_output(self, ctx: IOContext, chunk: StreamChunk):
        raise NotImplementedError


class ChunkIO(Generic[T]):
    def __init__(self,
                 fs: Frames,
                 chunk_size: Frames,
                 input_manager: InputManager,
                 output_manager: OutputManager,
                 name: str = "chunk-io"):
        self.fs = fs
        self.chunk_size = chunk_size
        self.input_manager = input_manager
        self.output_manager = output_manager
        self.name = name
        self.running = Value('i', 0)

    def start(self,
              in_queue: Optional[AudioChunkStream],
              out_queue: Optional[AudioChunkStream],
              metadata_queue: Optional[MetadataChunkStream]):
        with self.running.get_lock():
            self.running.value = 1
        input_ctx = self.input_manager.get_context()
        input_ctx.use_for_input()

        output_ctx = self.output_manager.get_context()
        output_ctx.use_for_output()

        with output_ctx:
            with input_ctx:
                out_thread = Thread(
                    name="chunk-output",
                    target=self.write_daemon,
                    args=(output_ctx, out_queue, metadata_queue),
                )
                out_queue.start()
                metadata_queue.start()
                out_thread.start()

                in_thread = Thread(
                    name="chunk-input",
                    target=self.read_daemon,
                    args=(input_ctx, in_queue),
                )
                in_queue.start()
                in_thread.start()

                out_thread.join()
                out_queue.stop()
                metadata_queue.stop()

                in_thread.join()
                in_queue.stop()

    def start_daemon(self,
                     in_queue: Optional[AudioChunkStream],
                     out_queue: Optional[AudioChunkStream],
                     metadata_queue: Optional[MetadataChunkStream]):
        def target(iq, oq, mq):
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self.start(iq, oq, mq)

        proc = Process(
            name=self.name,
            target=target,
            args=(in_queue, out_queue, metadata_queue),
        )
        proc.start()
        return proc

    def is_running(self):
        with self.running.get_lock():
            return self.running.value == 1

    def stop(self):
        with self.running.get_lock():
            self.running.value = 0

    def read_daemon(self, ctx: T, buffer_out: AudioChunkStream):
        print("starting input")
        cur_frame = 0
        try:
            while self.is_running():
                metadata = ChunkMetadata(
                    fs=self.fs,
                    start=cur_frame,
                    end=cur_frame + self.chunk_size,
                )
                metadata.round_trip_time.start()
                with metadata.audio_in:
                    buf = self.input_manager.read_input(ctx, metadata)

                chunk = StreamChunk(buf, metadata=metadata)
                metadata.input_send.start()
                buffer_out.put(chunk)
                cur_frame += self.chunk_size
        except Exception as e:
            print("error, shutting down input")
            raise e
        finally:
            self.stop()
            buffer_out.close()
        print("finished input")

    def write_daemon(self,
                     ctx: T,
                     buffer_in: AudioChunkStream,
                     metadata_out: Optional[MetadataChunkStream] = None):
        print("starting output")
        try:
            output_recv = MetadataTimer.started()
            for chunk in buffer_in:
                output_recv.stop()
                chunk.metadata.processor_send.stop()
                chunk.metadata.output_recv = output_recv
                with chunk.metadata.audio_out:
                    self.output_manager.write_output(ctx, chunk)
                chunk.metadata.round_trip_time.stop()
                if metadata_out is not None:
                    metadata_out.put(chunk.metadata)
                output_recv = MetadataTimer.started()
        except Exception as e:
            print("error, shutting down output")
            raise e
        finally:
            self.stop()
            if metadata_out is not None:
                metadata_out.close()
        print("finished output")


class StreamWorker:
    def __init__(self,
                 input_stream: AudioChunkStream,
                 output_stream: AudioChunkStream):
        self.input_stream = input_stream
        self.output_stream = output_stream

    def work(self):
        print("starting worker")
        try:
            total_frames = 0
            timer = MetadataTimer.started()
            for chunk in self.input_stream:
                timer.stop()
                metadata = chunk.metadata
                metadata.processor_recv = timer
                metadata.input_send.stop()
                with metadata.processing_time:
                    out = self.process(chunk)
                metadata.processor_send.start()
                self.output_stream.put(StreamChunk(out, metadata))
                total_frames = metadata.end
                timer = MetadataTimer.started()
        except Exception as e:
            print("error: shutting down processor")
            raise e
        finally:
            self.output_stream.close()
        print("shutting down worker")
        return total_frames

    def process(self, chunk: StreamChunk):
        raise NotImplementedError
