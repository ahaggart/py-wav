from typing import Type, Dict

from sources.Source import Source
from sources.aggregations.SequentialSource import SequentialSource
from sources.aggregations.AdditiveSource import AdditiveSource
from sources.transform.DilatedSource import DilatedSource
from sources.waveforms.SineSource import SineSource
from sources.waveforms.NoteSource import NoteSource
from sources.waveforms.SawSource import SawSource

__registered_sources: Dict[str, Type[Source]] = {
    "additive": AdditiveSource,
    "dilation": DilatedSource,
    "sine": SineSource,
    "sequential": SequentialSource,
    "saw": SawSource,
    "note": NoteSource,
}


def register(name: str, clazz: Type[Source]):
    if name in __registered_sources:
        raise NameError
    __registered_sources[name] = clazz


def get_registry() -> Dict[str, Type[Source]]:
    return __registered_sources.copy()
