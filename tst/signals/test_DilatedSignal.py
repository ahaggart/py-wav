from typing import List

from signals.BufferSignal import BufferSignal
from signals.DilatedSignal import DilatedSignal
from signals.OffsetSignal import OffsetSignal
from tst.SignalTestCase import SignalTestCase


class TestDilatedSignal(SignalTestCase):
    def setUp(self) -> None:
        self.test_fs = 1

    def create_dilated(self,
                       factor: float,
                       child_data: List[float],
                       offset: float = 0):
        base = BufferSignal(SignalTestCase.get_signal_data({
            "buffer": child_data,
            "fs": self.test_fs
        }))

        child = OffsetSignal(SignalTestCase.get_signal_data({
            "offset": offset,
        }, resolved_refs={"child": base}))

        return DilatedSignal(SignalTestCase.get_signal_data({
            "factor": factor,
        }, resolved_refs={"child": child}))

    def test_no_dilation(self):
        signal = self.create_dilated(1, [0, 1, 2, 3, 4, 5])
        self.assertEqual((0, 6), signal.get_range(self.test_fs))
        self.assertEqual(6, signal.get_period(self.test_fs))
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4, 5],
            signal.get_temporal(self.test_fs, 0, 6)
        )
        self.assertEqualsNumpy(
            [0, 0, 0, 0, 1, 2, 3, 4, 5],
            signal.get_temporal(self.test_fs, -3, 6)
        )
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4, 5, 0, 0, 0],
            signal.get_temporal(self.test_fs, 0, 9)
        )

    def test_positive_dilation(self):
        signal = self.create_dilated(1.875, [0, 1, 2, 3, 4, 5, 6, 7])
        self.assertEqual((0, 15), signal.get_range(self.test_fs))
        self.assertEqual(15, signal.get_period(self.test_fs))
        self.assertEqualsNumpy(
            [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7],
            signal.get_temporal(self.test_fs, 0, 15),
        )

    def test_negative_dilation(self):
        signal = self.create_dilated(0.6, [0, 1, 2, 3, 4])
        self.assertEqual((0, 3), signal.get_range(self.test_fs))
        self.assertEqual(3, signal.get_period(self.test_fs))
        self.assertEqualsNumpy(
            [0, 2, 4],
            signal.get_temporal(self.test_fs, 0, 3),
        )

    def test_offset_dilation(self):
        # TODO: This is finicky due to rounding stuff
        signal = self.create_dilated(1.875, [0, 1, 2, 3, 4, 5], offset=2)
        self.assertEqual((0, 15), signal.get_range(self.test_fs))
        self.assertEqual(15, signal.get_period(self.test_fs))
        self.assertEqualsNumpy(
            [0, 0, 0, 0, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
            signal.get_temporal(self.test_fs, 0, 15),
        )
