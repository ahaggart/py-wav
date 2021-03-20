from typing import NewType, Tuple

Seconds = NewType("Seconds", float)
Frames = NewType("Frames", int)
Partial = NewType("Partial", float)
FrameRange = NewType("FrameRange", Tuple[Partial, Partial])
Hz = NewType("Hz", float)
