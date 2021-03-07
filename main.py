import json
from typing import Dict, Type

from Signal import Signal
from SignalCache import SignalCache
from SignalData import SignalData
from SignalGraph import SignalGraph
from SignalManager import SignalManager
from output import play_signal
from signals.OffsetSignal import OffsetSignal
from signals.WavSignal import WavSignal

fs = 44100

with open("resources/signals.json") as f:
    signals_raw = json.load(f)

signal_data = [SignalData(d) for d in signals_raw]

initializers: Dict[str, Type[Signal]] = {
    "wav": WavSignal,
    "offset": OffsetSignal,
}

graph = SignalGraph(signal_data)
cache = SignalCache(initializers, signal_data)
manager = SignalManager(graph, cache)

signals = cache.signals

offset_signal = signals['offset-2']

play_signal(offset_signal, fs)
