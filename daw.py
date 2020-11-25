#!/usr/bin/env python
import numpy as np

from SourceState import SourceState
from custom_types import Seconds
from mapper.mapper import SourceParser, save
from output import play_from_source
import matplotlib.pyplot as plt

from mapper.registry import get_registry


if __name__ == "__main__":
    fs = 44100  # 44100 samples per second

    parser = SourceParser(get_registry())
    root = parser.parse("resources/sample.json")

    root_state = SourceState(
        offset=Seconds(0),
        dilation_factor=1.0,
        depth=0,
    )

    root.set_state(root_state)

    save(root, "out/song.json")

    play_from_source(root, fs)
    duration = root.get_duration(fs)
    # x = np.linspace(0, duration, duration)
    # plt.plot(x, root.get_buffer(fs, 0, duration))
    # plt.show()
