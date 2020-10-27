#!/usr/bin/env python

from mapper.mapper import SourceParser, save
from output import play_from_source
from mapper.registry import get_registry


if __name__ == "__main__":
    fs = 44100  # 44100 samples per second

    parser = SourceParser(get_registry())
    root = parser.parse("resources/in_the_hall_of_the_mountain_king.json")

    save(root, "out/song.json")

    play_from_source(root, fs)
