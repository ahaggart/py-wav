#!/usr/bin/env python

from parser import SourceParser
from output import play_from_source
from sources.registry import get_registry

if __name__ == "__main__":
    fs = 44100  # 44100 samples per second

    parser = SourceParser(get_registry())
    root = parser.parse("resources/song.json")

    play_from_source(root, fs)
