import json
from json import JSONEncoder
from typing import Dict, Type

from mapper.Mappable import Mappable


def tree_print(msg: str, depth: int):
    print("-" * depth + msg)


def save(source: Mappable, file: str):
    with open(file, 'w') as f:
        json.dump(source, f, cls=SourceEncoder)


class SourceEncoder(JSONEncoder):
    def default(self, o):
        return o.get_params()


class SourceParser:
    def __init__(self, registry: Dict[str, Type[Mappable]]):
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

        unpacked = {"type": type_name}

        for key in raw:
            unpacked[key] = self.unpack(raw[key], depth=depth+1, name=key)

        try:
            return clazz(**unpacked)
        except TypeError:
            print(f"Error parsing {type_name}")
            raise
