from typing import List

from custom_types import Frames
from signals.BufferSignal import BufferSignal
from signals.OffsetSignal import OffsetSignal
from signals.VariableOffsetSignal import VariableOffsetSignal
from tst.SignalTestCase import SignalTestCase


class TestVariableOffsetSignal(SignalTestCase):
    def setUp(self) -> None:
        self.test_fs = 1

    def get_signal(self,
                   child_data: List[float],
                   offset_data: List[float],
                   constant_offset: Frames = 0,
                   ):
        base = BufferSignal(self.get_signal_data({
            "buffer": child_data,
            "fs": self.test_fs,
        }))

        variable_offset = BufferSignal(self.get_signal_data({
            "buffer": offset_data,
            "fs": self.test_fs,
        }))

        constant_offset = OffsetSignal(self.get_signal_data({
            "offset": constant_offset,
        }, resolved_refs={"child": variable_offset}))

        return VariableOffsetSignal(self.get_signal_data(
            {}, resolved_refs={"child": base, "offset": constant_offset}
        ))

    def test_zero_offset(self):
        signal = self.get_signal(
            [1, 2, 3, 4, 5],
            [0, 0, 0, 0, 0],
        )
        self.assertEqual(5, signal.get_period(self.test_fs))
        self.assertEqual((0, 5), signal.get_range(self.test_fs))
        self.assertEqualsNumpy(
            [1, 2, 3, 4, 5],
            signal.get_temporal(self.test_fs, 0, 5)
        )
        self.assertEqualsNumpy(
            [0, 0, 1, 2, 3, 4, 5, 0, 0],
            signal.get_temporal(self.test_fs, -2, 7)
        )
        self.assertEqualsNumpy(
            [3, 4],
            signal.get_temporal(self.test_fs, 2, 4)
        )

    def test_constant_positive_offset(self):
        signal = self.get_signal(
            [1, 2, 3, 4, 5],
            [1, 1, 1, 1, 1, 1],
        )
        self.assertEqual(6, signal.get_period(self.test_fs))
        self.assertEqual((0, 6), signal.get_range(self.test_fs))
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4, 5],
            signal.get_temporal(self.test_fs, 0, 6)
        )
        self.assertEqualsNumpy(
            [0, 0, 0, 1, 2, 3, 4, 5, 0, 0],
            signal.get_temporal(self.test_fs, -2, 8)
        )
        self.assertEqualsNumpy(
            [2, 3],
            signal.get_temporal(self.test_fs, 2, 4)
        )

    def test_constant_negative_offset(self):
        signal = self.get_signal(
            [1, 2, 3, 4, 5],
            [-1, -1, -1, -1, -1, -1], -1
        )
        self.assertEqual(6, signal.get_period(self.test_fs))
        self.assertEqual((-1, 5), signal.get_range(self.test_fs))
        self.assertEqualsNumpy(
            [1, 2, 3, 4, 5, 0],
            signal.get_temporal(self.test_fs, -1, 5)
        )
        self.assertEqualsNumpy(
            [0, 0, 1, 2, 3, 4, 5, 0, 0, 0],
            signal.get_temporal(self.test_fs, -3, 7)
        )
        self.assertEqualsNumpy(
            [4, 5],
            signal.get_temporal(self.test_fs, 2, 4)
        )

    def test_variable_offset_inward(self):
        signal = self.get_signal(
            [+0,  1,  2,  3,  4,  5,  6,  7,  8,  9],
            [-1, -1, -1,  0,  0,  0,  0,  0,  1,  1],
        )
        self.assertEqual(10, signal.get_period(self.test_fs))
        self.assertEqual((0, 10), signal.get_range(self.test_fs))
        self.assertEqualsNumpy(
            [1, 2, 3, 3, 4, 5, 6, 7, 7, 8],
            signal.get_temporal(self.test_fs, 0, 10),
        )
        self.assertEqualsNumpy(
            [0, 0, 1, 2, 3, 3, 4, 5, 6, 7, 7, 8, 0, 0],
            signal.get_temporal(self.test_fs, -2, 12),
        )

    def test_variable_offset_outward(self):
        signal = self.get_signal(
            [+0,  1,  2,  3,  4,  5,  6,  7,  8,  9],
            [+1,  1,  0,  0,  0,  0,  0,  0, -1, -1],
        )
        self.assertEqual(10, signal.get_period(self.test_fs))
        self.assertEqual((0, 10), signal.get_range(self.test_fs))
        self.assertEqualsNumpy(
            [0, 0, 2, 3, 4, 5, 6, 7, 9, 0],
            signal.get_temporal(self.test_fs, 0, 10),
        )
        self.assertEqualsNumpy(
            [0, 0, 0, 0, 2, 3, 4, 5, 6, 7, 9, 0, 0, 0],
            signal.get_temporal(self.test_fs, -2, 12),
        )

    def test_variable_offset_big_middle(self):
        signal = self.get_signal(
            [+0,  1,  2,  3,  4,  5,  6,  7,  8,  9],
            [+0,  0,  0,  0,  6, -6,  0,  0,  0,  0],
        )
        self.assertEqual(10, signal.get_period(self.test_fs))
        self.assertEqual((0, 10), signal.get_range(self.test_fs))
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 0, 0, 6, 7, 8, 9],
            signal.get_temporal(self.test_fs, 0, 10),
        )

    def test_variable_offset_far_up(self):
        signal = self.get_signal(
            [+0,  1,  2,  3,  4],
            [+0,  0,  0,  0,  0,  0,  0,  0,  0,  5],
        )
        self.assertEqual(10, signal.get_period(self.test_fs))
        self.assertEqual((0, 10), signal.get_range(self.test_fs))
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4, 0, 0, 0, 0, 4],
            signal.get_temporal(self.test_fs, 0, 10),
        )
        self.assertEqualsNumpy(
            [0, 0, 0, 1, 2, 3, 4, 0, 0, 0, 0, 4, 0, 0],
            signal.get_temporal(self.test_fs, -2, 12),
        )

    def test_variable_offset_far_down(self):
        signal = self.get_signal(
            [+0,  1,  2,  3,  4],
            [-6,  0,  0,  0,  0,  0,  0,  0,  0,  0], -5
        )
        self.assertEqual(10, signal.get_period(self.test_fs))
        self.assertEqual((-5, 5), signal.get_range(self.test_fs))
        self.assertEqualsNumpy(
            [1, 0, 0, 0, 0, 0, 1, 2, 3, 4],
            signal.get_temporal(self.test_fs, -5, 5),
        )
        self.assertEqualsNumpy(
            [0, 0, 1, 0, 0, 0, 0, 0, 1, 2, 3, 4, 0, 0],
            signal.get_temporal(self.test_fs, -7, 7),
        )
