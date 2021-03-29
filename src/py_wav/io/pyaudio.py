from __future__ import annotations

from typing import Optional, ContextManager

import numpy as np
import pyaudio

from custom_types import Hz, Frames
from py_wav.io.streaming import StreamChunk, ChunkMetadata, AudioChunkStream, MetadataChunkStream, ChunkIO, \
    MetadataTimer


class PyAudioContext(ContextManager):
    def __init__(self, fs: Hz, channels: int, chunk_size: Frames,
                 do_input: bool, do_output: bool):
        self.chunk_size = chunk_size
        self.fs = int(fs)
        self.channels = int(channels)
        self.do_input = do_input
        self.do_output = do_output
        self.p = None
        self.stream = None

    def __enter__(self):
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
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


class PyAudioStreaming(ChunkIO[PyAudioContext]):
    def __init__(self, fs: Hz, channels: int, chunk_size: Frames):
        ChunkIO.__init__(self, fs, chunk_size, name="pyaudio")
        self.chunk_size = chunk_size
        self.fs = int(fs)
        self.channels = int(channels)

    def read_input(self, ctx: PyAudioContext):
        in_data = ctx.stream.read(self.chunk_size)
        return np.frombuffer(in_data, dtype=np.float32)

    def write_output(self, ctx: PyAudioContext, chunk: StreamChunk):
        frames = chunk.buf.astype(np.float32).tobytes()
        ctx.stream.write(frames, num_frames=len(chunk.buf))

    def streaming_context(self, do_input: bool, do_output: bool) -> PyAudioContext:
        return PyAudioContext(
            fs=self.fs,
            channels=self.channels,
            chunk_size=self.chunk_size,
            do_input=do_input,
            do_output=do_output,
        )
