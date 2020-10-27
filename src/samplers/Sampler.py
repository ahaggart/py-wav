class Sampler:
    def __init__(self, parent):
        self.parent = parent

    def sample(self, source, fs, start, end):
        return self.parent.sample(source, fs, start, end)

    def get_fs(self):
        return self.parent.get_fs()


class RootSampler(Sampler):
    def __init__(self, fs):
        Sampler.__init__(self, self)
        self.fs = fs

    def sample(self, source, fs, start, end):
        return source.get_buffer(fs, start, end)

    def get_fs(self):
        return self.fs
