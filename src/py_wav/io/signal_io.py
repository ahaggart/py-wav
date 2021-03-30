from Signal import Signal
from py_wav.io.streaming import StreamWorker, AudioChunkStream, StreamChunk, InputManager, DummyContext, ChunkMetadata
from signals.StreamingSignal import StreamingSignal


class SignalStreamWorker(StreamWorker):
    def __init__(self,
                 input_stream: AudioChunkStream,
                 input_signal: StreamingSignal,
                 output_signal: Signal,
                 output_stream: AudioChunkStream):
        StreamWorker.__init__(self, input_stream, output_stream)
        self.input_signal = input_signal
        self.output_signal = output_signal

    def process(self, chunk: StreamChunk):
        metadata = chunk.metadata
        fs = metadata.fs
        self.input_signal.put_data(metadata.start, metadata.end, chunk.buf)
        return self.output_signal.get_temporal(fs, metadata.end-metadata.start, metadata.end)


class SignalInputManager(InputManager):
    def __init__(self, signal: Signal):
        self.signal = signal

    def read_input(self, ctx: DummyContext, metadata: ChunkMetadata):
        return self.signal.get_temporal(metadata.fs, metadata.start, metadata.end)

    def get_context(self) -> DummyContext:
        return DummyContext()
