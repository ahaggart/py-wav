from mapper.Mappable import Mappable


class Filter(Mappable):
    def __init__(self):
        Mappable.__init__(self)
        self.create_mapping()

    def apply(self, fs, buffer):
        raise NotImplementedError
