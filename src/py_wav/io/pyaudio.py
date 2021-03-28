from __future__ import annotations

from typing import Optional, ContextManager

import numpy as np
import pyaudio

from custom_types import Hz, Frames
from py_wav.io.streaming import StreamChunk, ChunkMetadata, AudioChunkStream, MetadataChunkStream, ChunkIO


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
        ChunkIO.__init__(self, "pyaudio")
        self.chunk_size = chunk_size
        self.fs = int(fs)
        self.channels = int(channels)

    def read_input(self,
                   ctx: PyAudioContext,
                   buffer_out: AudioChunkStream):
        print("starting input")
        audio_in = ctx.stream
        cur_frame = 0
        while self.is_running():
            metadata = ChunkMetadata(
                fs=self.fs,
                start=cur_frame,
                end=cur_frame + self.chunk_size,
            )

            in_data = audio_in.read(self.chunk_size)
            with metadata.input_time:
                buf = np.frombuffer(in_data, dtype=np.float32)

            chunk = StreamChunk(buf, metadata=metadata)
            metadata.round_trip_time.start()
            metadata.input_wait.start()
            buffer_out.put(chunk)
            cur_frame += self.chunk_size
        buffer_out.close()
        print("finished input")

    def write_output(self,
                     ctx: PyAudioContext,
                     buffer_in: AudioChunkStream,
                     metadata_out: Optional[MetadataChunkStream] = None):
        print("starting output")
        audio_out = ctx.stream
        for chunk in buffer_in:
            chunk.metadata.output_wait.stop()
            chunk.metadata.round_trip_time.stop()
            with chunk.metadata.output_time:
                frames = chunk.buf.astype(np.float32).tobytes()
                audio_out.write(frames, num_frames=len(chunk.buf))
            if metadata_out is not None:
                metadata_out.put(chunk.metadata)
        if metadata_out is not None:
            metadata_out.close()
        print("finished output")

    def streaming_context(self, do_input: bool, do_output: bool) -> PyAudioContext:
        return PyAudioContext(
            fs=self.fs,
            channels=self.channels,
            chunk_size=self.chunk_size,
            do_input=do_input,
            do_output=do_output,
        )
