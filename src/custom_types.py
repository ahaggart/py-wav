from typing import NewType, Union, Optional, Tuple

Seconds = NewType("Seconds", float)
Frames = NewType("Frames", int)
Partial = NewType("Partial", float)
FrameRange = NewType("FrameRange", Tuple[Optional[Partial], Optional[Partial]])
Hz = NewType("Hz", float)
