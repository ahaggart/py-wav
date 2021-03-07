from __future__ import annotations

from typing import List

import Signal
import SignalCache


class SignalManager:
    def __init__(self, cache: SignalCache.SignalCache):
        self.signals = None
        self.cache = cache
        self.references = {}

    def setup(self, signals: List[Signal.Signal]):
        self.signals = {signal.data.uuid: signal for signal in signals}

    def get_signal(self,
                   uuid: str,
                   caller_uuid: str,
                   primary_domain: str = None) -> Signal.Signal:
        return Signal.WrapperSignal(uuid, self)

    def _get_signal(self, uuid: str) -> Signal.Signal:
        return self.signals[uuid]


