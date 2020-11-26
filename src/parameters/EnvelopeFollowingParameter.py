from collections import deque

import numpy as np
from scipy.signal import hilbert

from custom_types import Hz, Frames
from parameters.Parameter import Parameter


class EnvelopeFollowingParameter(Parameter):
    def __init__(self, freq: Hz, p: Parameter, **kwargs):
        Parameter.__init__(self)
        self.create_mapping()
        self.freq = freq
        self.p = p

    def get_state(self):
        return self.p.get_state()

    def get_period(self, fs: Frames) -> Frames:
        return self.p.get_period(fs)

    def get_buffer(self, fs, start, end):
        base = self.p.get_buffer(fs, start, end)
        return self.env_hilbert(fs, base)

    def env_hilbert(self, fs, base):
        return np.abs(hilbert(base))

    def env_rolling_max(self, fs, base):
        print("start envelope")
        window_size = int(fs / self.freq) + 1
        dq = deque(maxlen=window_size)

        mins = np.zeros(len(base))

        i = 0
        for v in base:
            if len(dq) != 0 and dq[0][0] <= (i - window_size):
                dq.popleft()

            while len(dq) != 0 and dq[-1][1] < v:
                dq.pop()

            dq.append((i, v))
            curr_min = dq[0][1]
            mins[i] = curr_min
            i += 1

        print("stop envelope")
        return mins


"""
at every step:

  if (!Deque.Empty) and (Deque.Head.Index <= CurrentIndex - T) then 
     Deque.ExtractHead;
  //Head is too old, it is leaving the window

  while (!Deque.Empty) and (Deque.Tail.Value > CurrentValue) do
     Deque.ExtractTail;
  //remove elements that have no chance to become minimum in the window

  Deque.AddTail(CurrentValue, CurrentIndex); 
  CurrentMin = Deque.Head.Value
  //Head value is minimum in the current window
"""