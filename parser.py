from typing import List, Dict, Tuple

registered_classes = {}

def tree_print(msg: str, depth: int):
    print("-" * depth + msg)

def unpack(obj, depth, name="Value"):
    if isinstance(obj, dict):
        return construct(obj, depth=depth)
    elif isinstance(obj, list):
        tree_print("unpacking a list", depth)
        return [unpack(i, depth=depth+1) for i in obj]
    else:
        tree_print(f"{name}: {obj}", depth)
        return obj

def construct(raw: Dict, depth=0):
    if "type" not in raw:  # this is a data object
        return raw

    type_name = raw.pop("type")
    tree_print(f"Node: {type_name}", depth)

    clazz = registered_classes[type_name]

    unpacked = {}
    
    for key in raw:
        unpacked[key] = unpack(raw[key], depth=depth+1, name=key)

    return clazz(**unpacked)