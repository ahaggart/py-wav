from typing import Optional
from unittest import TestCase

import numpy as np

from custom_types import Frames, FrameRange
from mixins.BufferMixins import TilingMixin


class TestBase(TilingMixin):
    def __init__(self, length: Frames, lower: Optional[Frames], upper: Optional[Frames]):
        TilingMixin.__init__(self)
        self.length = length
        self.lower = lower
        self.upper = upper

    def get_buffer(self, fs: Frames):
        return np.arange(self.length)

    def get_range(self, fs: Frames) -> FrameRange:
        return self.lower, self.upper


class TilingMixinTest(TestCase):
    def setUp(self) -> None:
        self.fs = 44100

    def assertEqualsNumpy(self, a1, a2, msg=None):
        self.assertTrue(
            np.array_equal(a1, a2),
            msg=f"{a1} != {a2}" + (msg if msg is not None else ""),
        )

    def do_baseline_tests(self, signal: TestBase):
        self.assertEqualsNumpy(
            np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
            signal.get_temporal(self.fs, 0, 10),
        )
        self.assertEqualsNumpy(
            np.array([4, 5, 6]),
            signal.get_temporal(self.fs, 4, 7),
        )
        self.assertEqualsNumpy(
            np.array([0, 1, 2, 3, 4]),
            signal.get_temporal(self.fs, 0, 5),
        )
        self.assertEqualsNumpy(
            np.array([5, 6, 7, 8, 9]),
            signal.get_temporal(self.fs, 5, 10),
        )

    def test_upper_lower_bounded(self):
        signal = TestBase(10, 0, 10)
        self.do_baseline_tests(signal)
        self.assertEqualsNumpy(
            np.array([0, 0, 0, 1, 2, 3]),
            signal.get_temporal(self.fs, -2, 4),
        )
        self.assertEqualsNumpy(
            np.array([8, 9, 0, 0]),
            signal.get_temporal(self.fs, 8, 12),
        )

    def test_upper_bounded(self):
        signal = TestBase(10, None, 10)
        self.do_baseline_tests(signal)
        self.assertEqualsNumpy(
            np.array([8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
            signal.get_temporal(self.fs, -2, 10),
        )
        self.assertEqualsNumpy(
            np.array([5, 6, 7, 8, 9]),
            signal.get_temporal(self.fs, -5, 0),
        )
        self.assertEqualsNumpy(
            np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9] * 4),
            signal.get_temporal(self.fs, -40, 0),
        )
        self.assertEqualsNumpy(
            np.array([8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0]),
            signal.get_temporal(self.fs, -2, 12),
        )
        self.assertEqualsNumpy(
            np.array([0, 0, 0, 0, 0]),
            signal.get_temporal(self.fs, 10, 15),
        )

    def test_lower_bounded(self):
        signal = TestBase(10, 0, None)
        self.do_baseline_tests(signal)
        self.assertEqualsNumpy(
            np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9] * 4),
            signal.get_temporal(self.fs, 0, 40),
        )
        self.assertEqualsNumpy(
            np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2]),
            signal.get_temporal(self.fs, 0, 13),
        )
        self.assertEqualsNumpy(
            np.array([0, 0, 0, 1, 2, 3]),
            signal.get_temporal(self.fs, -2, 4),
        )
        self.assertEqualsNumpy(
            np.array([0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2]),
            signal.get_temporal(self.fs, -2, 13),
        )
        self.assertEqualsNumpy(
            np.array([0, 1, 2, 3, 4]),
            signal.get_temporal(self.fs, 10, 15),
        )

    def test_unbounded(self):
        signal = TestBase(10, None, None)
        self.do_baseline_tests(signal)
        self.assertEqualsNumpy(
            np.array([8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2]),
            signal.get_temporal(self.fs, -2, 13),
        )
        self.assertEqualsNumpy(
            np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 0] * 4),
            signal.get_temporal(self.fs, -19, 21),
        )
        self.assertEqualsNumpy(
            np.array([5, 6, 7, 8, 9]),
            signal.get_temporal(self.fs, -5, 0),
        )
        self.assertEqualsNumpy(
            np.array([0, 1, 2, 3, 4]),
            signal.get_temporal(self.fs, 10, 15),
        )