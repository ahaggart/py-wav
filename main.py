import logging

import matplotlib.pyplot as plt
import numpy as np

# noinspection PyUnresolvedReferences
import signals as _
from SignalCache import SignalCache
from SignalGraph import SignalGraph
from SignalManager import SignalManager
from SignalRegistry import get_registry
from Workspace import Workspace
from output import play_signal
from util.frames import to_frames

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


fs = 44100

registry = get_registry()
graph = SignalGraph()
manager = SignalManager(SignalCache)

workspace = Workspace("resources/signals.json", manager, graph, registry)

workspace.initialize()

signals = manager.signals

restored_signal = manager.get_signal('dilated:2')
dilated_signal = manager.get_signal('dilated:0.5')
offset_signal = manager.get_signal('offset:2')
base_signal = manager.get_signal('wav')
var_offset_signal = manager.get_signal('var_offset')
sine_signal = manager.get_signal('sine')
selected_signal = var_offset_signal

diff = np.abs(np.subtract(
    base_signal.get_temporal(fs, 0, to_frames(base_signal.get_period(fs))),
    var_offset_signal.get_temporal(fs, 0, to_frames(base_signal.get_period(fs))),
))

PLOT = True

if PLOT:
    extras = 1
    dur = to_frames(dilated_signal.get_period(fs))
    fig, (ax) = plt.subplots(len(signals)+extras, 1)
    ax[0].plot(diff)
    for i, signal in zip(range(len(signals)), signals.values()):
        sub_ax = ax[i+extras]
        print(f"plotting {signal.data.uuid}")
        sub_ax.plot(signal.get_temporal(fs, 0, dur))
        sub_ax.title.set_text(signal.data.uuid)
    plt.show()
else:
    play_signal(selected_signal, fs, end=5*fs)
