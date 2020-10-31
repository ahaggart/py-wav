#!/usr/bin/env python
import numpy as np

from mapper.mapper import SourceParser, save
from output import play_from_source
import matplotlib.pyplot as plt

from mapper.registry import get_registry


if __name__ == "__main__":
    fs = 44100  # 44100 samples per second

    parser = SourceParser(get_registry())
    root = parser.parse("resources/sample.json")

    save(root, "out/song.json")

    play_from_source(root, fs)
    duration = root.get_duration(fs)
    x = np.linspace(0, duration, duration)
    plt.plot(x, root.get_buffer(fs, 0, duration))
    plt.show()
