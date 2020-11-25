from core.Stateful import Stateful


class Transform(Stateful):
    def __init__(self):
        Stateful.__init__(self)
        self.create_mapping()

    def apply(self, fs, buffer):
        raise NotImplementedError
