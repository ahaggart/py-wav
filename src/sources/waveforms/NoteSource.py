from sources.Source import Source

notes = {
    "A": 440.00,
    "A#": 466.16,
    "Bb": 466.16,
    "B": 493.88,
    "C": 523.25,
    "C#": 554.37,
    "Db": 554.37,
    "D": 587.33,
    "D#": 622.25,
    "Eb": 622.25,
    "E": 659.25,
    "F": 698.46,
    "F#": 739.99,
    "Gb": 739.99,
    "G": 783.99,
    "G#": 830.61,
    "Ab": 830.61,
}


class NoteSource(Source): 
    sources = {}  # to be populated in __init__.py
   
    def __init__(self, name: str, output: str, seconds: float, octave: int = 0, **kwargs):
        Source.__init__(self)
        self.create_params()
        freq = notes[name]*(2**octave)
        clazz = NoteSource.sources[output]
        self.source = clazz(freq=freq, seconds=seconds)

    def get_buffer(self, fs, start, end):
        return self.source.get_buffer(fs, start, end)

    def get_duration(self, fs):
        return self.source.get_duration(fs)
