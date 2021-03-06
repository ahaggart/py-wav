from typing import Type, Dict

from parameters.spectral.FourierParameter import FourierParameter
from parameters.SourceParameter import SourceParameter
from parameters.SlidingParameter import SlidingParameter
from mapper.Mappable import Mappable
from sources.WavSource import WavSource
from sources.aggregations.SequentialSource import SequentialSource
from sources.aggregations.AdditiveSource import AdditiveSource
from sources.transform.DilatedSource import DilatedSource
from sources.transform.TransformedSource import TransformedSource
from sources.waveforms.BezierSource import BezierSource
from sources.waveforms.SineSource import SineSource
from sources.waveforms.NoteSource import NoteSource
from sources.waveforms.SawSource import SawSource
from transforms.FourierTransform import FourierTransform
from transforms.ScalingTransform import ScalingTransform
from transforms.filters.BeadingFilter import BeadingFilter
from transforms.filters.HarmonicFilter import HarmonicFilter

__registered_sources: Dict[str, Type[Mappable]] = {
    "additive": AdditiveSource,
    "dilation": DilatedSource,
    "sine": SineSource,
    "sequential": SequentialSource,
    "saw": SawSource,
    "note": NoteSource,
    "transformed": TransformedSource,
    "bezier": BezierSource,

    "s_wav": WavSource,

    "fourier": FourierTransform,

    "t_scaling": ScalingTransform,

    "harmonic": HarmonicFilter,
    "beading": BeadingFilter,

    "p_sliding": SlidingParameter,
    "p_source": SourceParameter,
    "p_fourier": FourierParameter,
}


def register(name: str, clazz: Type[Mappable]):
    if name in __registered_sources:
        raise NameError
    __registered_sources[name] = clazz


def get_registry() -> Dict[str, Type[Mappable]]:
    return __registered_sources.copy()
