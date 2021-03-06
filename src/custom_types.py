from typing import NewType, Union, Optional, Tuple

Seconds = NewType("seconds", float)
Frames = NewType("frames", int)
FrameRange = NewType("framerange", Tuple[Optional[Frames], Optional[Frames]])
Hz = NewType("hz", float)
