from sources.registry import get_registry
from sources.waveforms.NoteSource import NoteSource
NoteSource.sources = get_registry()
