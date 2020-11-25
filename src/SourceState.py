from copy import copy

from custom_types import Seconds


class SourceState:
    def __init__(self,
                 offset: Seconds = 0,
                 dilation_factor: float = 1.0,
                 depth: int = 0):
        self.offset = offset
        self.dilation_factor = dilation_factor
        self.depth = depth

    def copy(self):
        return copy(self)

    def with_offset(self, offset: Seconds):
        cpy = self.copy()
        cpy.offset += self.dilation_factor * offset
        return cpy

    def with_dilation(self, dilation_factor: float):
        cpy = self.copy()
        cpy.dilation_factor *= dilation_factor
        return cpy

    def with_depth(self, depth: int):
        cpy = self.copy()
        cpy.depth = depth
        return cpy
