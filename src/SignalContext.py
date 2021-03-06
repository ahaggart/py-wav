from SignalCache import SignalCache
from SignalManager import SignalManager


class SignalContext:
    def __init__(self, cache: SignalCache, manager: SignalManager):
        self.cache = cache
        self.manager = manager
