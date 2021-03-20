from typing import List

from custom_types import Seconds
from signals.BufferSignal import BufferSignal
from signals.TiledSignal import TiledSignal
from tst.SignalTestCase import SignalTestCase


class TestTiledSignal(SignalTestCase):
    def setUp(self) -> None:
        self.test_fs = 1

    def create_signal(self,
                      lower: Seconds,
                      upper: Seconds,
                      child_data: List[float]
                      ):
        child = BufferSignal(SignalTestCase.get_signal_data({
            "buffer": child_data,
            "fs": self.test_fs,
        }))

        return TiledSignal(SignalTestCase.get_signal_data({
            "lower": lower,
            "upper": upper,
        }, resolved_refs={"child": child}))

    def test_forward(self):
        signal = self.create_signal(0, 15, [0, 1, 2, 3, 4])
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4],
            signal.get_temporal(self.test_fs, 0, 5)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4] * 2,
            signal.get_temporal(self.test_fs, 0, 10)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4] * 3,
            signal.get_temporal(self.test_fs, 0, 15)
        )
        self.assertEqualsNumpy(
            [0, 0, 0, 0, 1, 2, 3, 4],
            signal.get_temporal(self.test_fs, -3, 5)
        )

    def test_backward(self):
        signal = self.create_signal(-105, 5, [0, 1, 2, 3, 4])
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4],
            signal.get_temporal(self.test_fs, 0, 5)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4] * 2,
            signal.get_temporal(self.test_fs, -5, 5)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4] * 3,
            signal.get_temporal(self.test_fs, -10, 5)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4],
            signal.get_temporal(self.test_fs, -105, -100)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4, 0, 0, 0],
            signal.get_temporal(self.test_fs, 0, 8)
        )

    def test_both(self):
        signal = self.create_signal(-105, 105, [0, 1, 2, 3, 4])
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4],
            signal.get_temporal(self.test_fs, 0, 5)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4] * 2,
            signal.get_temporal(self.test_fs, 0, 10)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4] * 3,
            signal.get_temporal(self.test_fs, -5, 10)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4],
            signal.get_temporal(self.test_fs, 100, 105)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4],
            signal.get_temporal(self.test_fs, -105, -100)
        )
