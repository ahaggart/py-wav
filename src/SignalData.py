from __future__ import annotations
from typing import Dict

import Signal


class SignalData:
    def __init__(self, data: Dict):
        self.uuid = data['uuid']
        self.data = data
        self.type_name = self.data['type']
        self.raw_refs = data.get('refs', {})
        self.resolved_refs: Dict[str, Signal.Signal] = {}

    def set_refs(self, refs: Dict[str, Signal.Signal]):
        self.resolved_refs = refs
