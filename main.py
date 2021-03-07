import json

from Signal import Signal
from SignalCache import SignalCache, CachedSignal
from SignalContext import SignalContext
from SignalData import SignalData
from SignalGraph import SignalGraph
from SignalManager import SignalManager
from output import play_signal
from signals.OffsetSignal import OffsetSignal
from signals.WavSignal import WavSignal

fs = 44100
graph = SignalGraph()
cache = SignalCache()
manager = SignalManager(cache)

with open("resources/signals.json") as f:
    signals_raw = json.load(f)


def initialize_class(cls, raw_data: dict) -> Signal:
    if 'refs' in raw_data:
        refs = {name: CachedSignal(uuid, cache) for name, uuid in raw_data['refs'].items()}
    else:
        refs = {}
    signal_data = SignalData(raw_data)
    signal_data.set_refs(refs)
    return cls(signal_data)


def initialize(raw_data: dict):
    type_name = raw_data['type']
    if type_name == 'wav':
        return initialize_class(WavSignal, raw_data)
    elif type_name == 'offset':
        return initialize_class(OffsetSignal, raw_data)
    else:
        raise KeyError


signals = [initialize(d) for d in signals_raw]

manager.setup(signals)
cache.setup(signals)

offset_signal = list(filter(lambda s: s.data.uuid == "offset-2", signals))[0]

play_signal(offset_signal, fs)
