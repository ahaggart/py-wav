class Sampler:
    def __init__(self, parent):
        self.parent = parent

    def sample(self, source, fs, start, end):
        return self.parent.sample(source, fs, start, end)


class RootSampler(Sampler):
    def __init__(self):
        Sampler.__init__(self, self)

    def sample(self, source, fs, start, end):
        return source.get_buffer(fs, start, end)
