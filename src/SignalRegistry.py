from typing import Dict, Type, NewType


class RegistryEntry:
    def __init__(self, name: str, ctor: Type):
        self.name = name
        self.ctor = ctor


Registry = Dict[str, RegistryEntry]

__registry: Registry = {}


def register(name: str, ctor: Type):
    __registry[name] = RegistryEntry(name, ctor)


def get_registry() -> Registry:
    return __registry.copy()


