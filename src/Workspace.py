import json
from typing import Dict

from SignalContext import SignalContext
from SignalGraph import SignalGraph
from SignalManager import SignalManager
from SignalRegistry import Registry


class Workspace:
    def __init__(self, file_name: str,
                 manager: SignalManager,
                 graph: SignalGraph,
                 registry: Registry):
        self.contexts = self.load_from_file(file_name)
        self.manager = manager
        self.graph = graph
        self.registry = registry

    def load_from_file(self, file_name: str) -> Dict[str, SignalContext]:
        with open(file_name) as f:
            project_raw = json.load(f)
            signal_data = [SignalContext(d) for d in project_raw]
            return {c.uuid: c for c in signal_data}

    def initialize(self):
        for context in self.contexts.values():
            self.graph.put_vertex(context.uuid, context.raw_refs.values())

        for uuid in self.graph.traverse():
            context = self.contexts[uuid]
            for name, ref in context.raw_refs.items():
                context.set_ref(name, self.manager.resolve_ref(ref))
            signal = self.registry[context.type_name].ctor(context)
            self.manager.put_signal(signal)
