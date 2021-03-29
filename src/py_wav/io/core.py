from multiprocessing import Pipe
from multiprocessing import Queue
from typing import Generic, Generator, Optional, TypeVar, Iterable

T = TypeVar("T")


class ChunkStream(Generic[T]):
    def __init__(self, max_depth=0):
        self.queue = Queue(maxsize=max_depth)

    def __iter__(self) -> Iterable[T]:
        for chunk in iter(self.get, None):
            yield chunk

    def start(self):
        pass

    def stop(self):
        pass

    def get(self, block=True, timeout=None):
        return self.queue.get(block, timeout)

    def put(self, chunk: Optional[T], block=True, timeout=None):
        self.queue.put(chunk, block, timeout)

    def close(self):
        self.put(None)
