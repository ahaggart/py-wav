from typing import Type, Dict

from mapper.Mappable import Mappable
from sources.aggregations.SequentialSource import SequentialSource
from sources.aggregations.AdditiveSource import AdditiveSource
from sources.transform.DilatedSource import DilatedSource
from sources.transform.TransformedSource import TransformedSource
from sources.waveforms.SineSource import SineSource
from sources.waveforms.NoteSource import NoteSource
from sources.waveforms.SawSource import SawSource
from transforms.FourierTransform import FourierTransform

__registered_sources: Dict[str, Type[Mappable]] = {
    "additive": AdditiveSource,
    "dilation": DilatedSource,
    "sine": SineSource,
    "sequential": SequentialSource,
    "saw": SawSource,
    "note": NoteSource,
    "transformed": TransformedSource,
    "fourier": FourierTransform,
}


def register(name: str, clazz: Type[Mappable]):
    if name in __registered_sources:
        raise NameError
    __registered_sources[name] = clazz


def get_registry() -> Dict[str, Type[Mappable]]:
    return __registered_sources.copy()
