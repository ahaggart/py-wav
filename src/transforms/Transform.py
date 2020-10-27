from mapper.Mappable import Mappable


class Transform(Mappable):
    def __init__(self):
        Mappable.__init__(self)
        self.create_params()

    def apply(self, fs, buffer):
        raise NotImplementedError
