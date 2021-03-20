from __future__ import annotations

import logging

from Signal import Signal
from core.SignalProvider import SignalProvider
from custom_types import Frames, FrameRange, Hz

log = logging.getLogger(__name__)


class CachedSignal(Signal):
    def __init__(self, uuid: str, cache: SignalCache):
        Signal.__init__(self, None)
        self.uuid = uuid
        self.cache = cache
        self.child = None

    def get_child(self) -> Signal:
        if self.child is None:
            self.child = self.cache.get_signal(self.uuid)
        return self.child

    def get_range(self, fs: Frames) -> FrameRange:
        return self.get_child().get_range(fs)

    def get_spectral(self, fs: Frames):
        return self.cache.get_spectral(self.uuid, fs)

    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        return self.cache.get_temporal(self.uuid, fs, start, end)

    def get_period(self, fs: Frames) -> Frames:
        return self.get_child().get_period(fs)


class SignalCache:
    def __init__(self, provider: SignalProvider):
        self.temporal = {}
        self.spectral = {}
        self.provider = provider

    def get_signal(self, uuid: str):
        return self.provider.get_signal(uuid)

    def get_temporal(self, uuid: str, fs: Hz, start: Frames, end: Frames):
        log.debug(f"Temporal request uuid={uuid} fs={fs} start={start} end={end}")
        return self.get_signal(uuid).get_temporal(fs, start, end)

    def get_spectral(self, uuid: str, fs: Hz):
        log.debug(f"Spectral request uuid={uuid} fs={fs}")
        return self.get_signal(uuid).get_spectral(fs)
