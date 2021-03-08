import json
from typing import Dict, Type

import matplotlib.pyplot as plt
import numpy as np

from Signal import Signal
from SignalCache import SignalCache
from SignalData import SignalData
from SignalGraph import SignalGraph
from SignalManager import SignalManager
from output import play_signal
from signals.DilatedSignal import DilatedSignal
from signals.OffsetSignal import OffsetSignal
from signals.WavSignal import WavSignal

fs = 44100

with open("resources/signals.json") as f:
    signals_raw = json.load(f)

signal_data = [SignalData(d) for d in signals_raw]

initializers: Dict[str, Type[Signal]] = {
    "wav": WavSignal,
    "offset": OffsetSignal,
    "dilated": DilatedSignal,
}

graph = SignalGraph(signal_data)
cache = SignalCache(initializers, signal_data)
manager = SignalManager(graph, cache)

signals = cache.signals

restored_signal = signals['dilated:2']
dilated_signal = signals['dilated:0.5']
offset_signal = signals['offset:-2']
base_signal = signals['wav']

diff = np.abs(np.subtract(
    base_signal.get_temporal(fs, 0, base_signal.get_period(fs)),
    restored_signal.get_temporal(fs, 0, base_signal.get_period(fs)),
))

PLOT = False

if PLOT:
    extras = 1
    dur = signals['dilated:2'].get_period(fs)
    fig, (ax) = plt.subplots(len(signals)+extras, 1)
    ax[0].plot(diff)
    for i, signal in zip(range(len(signals)), signals.values()):
        sub_ax = ax[i+extras]
        print(f"plotting {signal.data.uuid}")
        sub_ax.plot(signal.get_temporal(fs, 0, dur))
        sub_ax.title.set_text(signal.data.uuid)
    plt.show()
else:
    play_signal(offset_signal, fs)
