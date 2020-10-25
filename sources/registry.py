from sources.aggregations.SequentialSource import SequentialSource
from sources.aggregations.AdditiveSource import AdditiveSource
from sources.transforms.SpeedModifiedSource import SpeedModifiedSource
from sources.waveforms.SineSource import SineSource
from sources.waveforms.NoteSource import NoteSource
from sources.waveforms.SawSource import SawSource

registered_sources = {
    "additive": AdditiveSource,
    "speed": SpeedModifiedSource,
    "sine": SineSource,
    "sequential": SequentialSource,
    "saw": SawSource,
    "note": NoteSource,
}