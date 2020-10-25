import json
from typing import Dict, Type

from sources.Source import Source


def tree_print(msg: str, depth: int):
    print("-" * depth + msg)


class SourceParser:
    def __init__(self, registry: Dict[str, Type[Source]]):
        self.registry = registry

    def parse(self, file):
        with open(file) as song:
            raw = json.load(song)
        return self.construct(raw)

    def unpack(self, obj, depth, name="Value"):
        if isinstance(obj, dict):
            return self.construct(obj, depth=depth)
        elif isinstance(obj, list):
            tree_print("unpacking a list", depth)
            return [self.unpack(i, depth=depth+1) for i in obj]
        else:
            tree_print(f"{name}: {obj}", depth)
            return obj

    def construct(self, raw: Dict, depth=0):
        if "type" not in raw:  # this is a data object
            return raw

        type_name = raw.pop("type")
        tree_print(f"Node: {type_name}", depth)

        clazz = self.registry[type_name]

        unpacked = {}

        for key in raw:
            unpacked[key] = self.unpack(raw[key], depth=depth+1, name=key)

        return clazz(**unpacked)
