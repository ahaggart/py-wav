import json

from SignalCache import SignalCache
from SignalContext import SignalContext
from SignalData import SignalData
from SignalManager import SignalManager
from output import play_signal
from signals.OffsetSignal import OffsetSignal
from signals.WavSignal import WavSignal

fs = 44100
cache = SignalCache()
manager = SignalManager()
context = SignalContext(cache, manager)

with open("resources/signals.json") as f:
    signals_raw = json.load(f)


def initialize(raw_data: dict):
    type_name = raw_data['type']
    if type_name == 'wav':
        return WavSignal(context, SignalData(raw_data))
    elif type_name == 'offset':
        return OffsetSignal(context, SignalData(raw_data))
    else:
        raise KeyError


signals = [initialize(d) for d in signals_raw]

manager.setup(signals)

offset_signal = list(filter(lambda s: s.data.uuid == "offset+2", signals))[0]

play_signal(offset_signal, fs)
