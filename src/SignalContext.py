from __future__ import annotations

import SignalCache
import SignalManager


class SignalContext:
    def __init__(self, cache: SignalCache.SignalCache, manager: SignalManager.SignalManager):
        self.cache = cache
        self.manager = manager
