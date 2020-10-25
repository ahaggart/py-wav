from sources.Source import Source

class SpeedModifiedSource(Source):
    def __init__(self, modifier: float, child: Source):
        self.modifier = 1.0 / float(modifier)
        self.child = child

    def get_buffer(self, fs):
        return self.child.get_buffer(fs * self.modifier)

    def get_duration(self):
        return self.child.get_duration() * self.modifier