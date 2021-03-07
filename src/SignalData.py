from typing import Dict


class SignalData:
    def __init__(self, data: Dict):
        self.uuid = data['uuid']
        self.data = data
