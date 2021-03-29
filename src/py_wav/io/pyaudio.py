from __future__ import annotations

import numpy as np
import pyaudio

from custom_types import Hz, Frames
from py_wav.io.streaming import StreamChunk, InputManager, OutputManager, IOContext, ChunkMetadata


class PyAudioContext(IOContext):
    def __init__(self, fs: Hz, channels: int, chunk_size: Frames):
        self.chunk_size = chunk_size
        self.fs = int(fs)
        self.channels = int(channels)
        self.do_input = False
        self.do_output = False
        self.p = None
        self.stream = None
        self.counter = 0

    def use_for_input(self):
        self.do_input = True

    def use_for_output(self):
        self.do_output = True

    def __enter__(self):
        self.counter += 1
        if self.counter > 1:
            return self
        print("starting up pyaudio")
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=self.channels,
                                  rate=self.fs,
                                  input=self.do_input,
                                  output=self.do_output,
                                  frames_per_buffer=self.chunk_size)
        self.stream.start_stream()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.counter -= 1
        if self.counter > 0:
            return
        print("shutting down pyaudio")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


class PyAudioStreaming(InputManager, OutputManager):
    def __init__(self, fs: Hz, channels: int, chunk_size: Frames):
        self.chunk_size = chunk_size
        self.fs = int(fs)
        self.channels = int(channels)
        self.context = PyAudioContext(
            fs=self.fs,
            channels=self.channels,
            chunk_size=self.chunk_size,
        )

    def read_input(self, ctx: PyAudioContext, metadata: ChunkMetadata):
        in_data = ctx.stream.read(self.chunk_size)
        return np.frombuffer(in_data, dtype=np.float32)

    def write_output(self, ctx: PyAudioContext, chunk: StreamChunk):
        frames = chunk.buf.astype(np.float32).tobytes()
        ctx.stream.write(frames, num_frames=len(chunk.buf))

    def get_context(self) -> PyAudioContext:
        return self.context
