from parameters.Parameter import parametrize
from transforms.Transform import Transform


class ScalingTransform(Transform):
    def __init__(self, intensity, **kwargs):
        Transform.__init__(self)
        self.create_mapping()
        self.intensity = parametrize(intensity)

    def apply(self, fs, buffer):
        intensity = self.intensity.sample_out(fs, 0, len(buffer))
        return buffer * intensity
