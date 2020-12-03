class WithUUID:
    def __init__(self):
        self.uuid: str = "default"

    def set_uuid(self, uuid: str):
        self.uuid = uuid
