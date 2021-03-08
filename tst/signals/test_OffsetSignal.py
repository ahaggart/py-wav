from typing import List

from SignalData import SignalData
from custom_types import Seconds
from signals.BufferSignal import BufferSignal
from signals.OffsetSignal import OffsetSignal
from signals.TiledSignal import TiledSignal
from tst.SignalTestCase import SignalTestCase


class TestOffsetSignal(SignalTestCase):
    def setUp(self) -> None:
        self.test_fs = 1

    def create_signal(self, offset: Seconds, child_data: List[float]):
        child = BufferSignal(SignalTestCase.get_signal_data({
            "buffer":  child_data,
            "fs": self.test_fs,
        }))

        return OffsetSignal(SignalTestCase.get_signal_data({
            "offset": offset,
        }, resolved_refs={"child": child}))

    def create_signal_unbounded(self,
                                offset: Seconds,
                                child_data: List[float],
                                direction: str):
        base = BufferSignal(SignalTestCase.get_signal_data({
            "buffer":  child_data,
            "fs": self.test_fs,
        }))

        child = TiledSignal(SignalTestCase.get_signal_data({
            "direction": direction,
        }, resolved_refs={"child": base}))

        return OffsetSignal(SignalTestCase.get_signal_data({
            "offset": offset,
        }, resolved_refs={"child": child}))

    def test_zero_offset_bounded(self):
        offset = self.create_signal(0, [0, 1, 2, 3, 4])
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4],
            offset.get_temporal(self.test_fs, 0, 5)
        )

        self.assertEqual(
            (0, 5),
            offset.get_range(self.test_fs)
        )

    def test_offset_positive_bounded(self):
        offset = self.create_signal(4, [0, 1, 2, 3, 4])
        self.assertEqualsNumpy(
            [0, 0, 0, 0, 0, 1, 2, 3, 4],
            offset.get_temporal(self.test_fs, 0, 9)
        )
        self.assertEqual((0, 9), offset.get_range(self.test_fs))
        self.assertEqual(9, offset.get_period(self.test_fs))

    def test_offset_negative_bounded(self):
        offset = self.create_signal(-4, [0, 1, 2, 3, 4])
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4, 0, 0, 0, 0],
            offset.get_temporal(self.test_fs, -4, 5)
        )
        self.assertEqual((-4, 5), offset.get_range(self.test_fs))
        self.assertEqual(9, offset.get_period(self.test_fs))

    def test_unbounded_range(self):
        zero_lower = self.create_signal_unbounded(0, [0, 1, 2, 3, 4], "backward")
        self.assertEqual((None, 5), zero_lower.get_range(self.test_fs))
        self.assertEqual(5, zero_lower.get_period(self.test_fs))

        pos_lower = self.create_signal_unbounded(3, [0, 1, 2, 3, 4], "backward")
        self.assertEqual((None, 5), pos_lower.get_range(self.test_fs))
        self.assertEqual(5, pos_lower.get_period(self.test_fs))

        neg_lower = self.create_signal_unbounded(-3, [0, 1, 2, 3, 4], "backward")
        self.assertEqual((None, 5), neg_lower.get_range(self.test_fs))
        self.assertEqual(5, neg_lower.get_period(self.test_fs))

        zero_upper = self.create_signal_unbounded(0, [0, 1, 2, 3, 4], "forward")
        self.assertEqual((0, None), zero_upper.get_range(self.test_fs))
        self.assertEqual(5, zero_upper.get_period(self.test_fs))

        pos_upper = self.create_signal_unbounded(3, [0, 1, 2, 3, 4], "forward")
        self.assertEqual((0, None), pos_upper.get_range(self.test_fs))
        self.assertEqual(5, pos_upper.get_period(self.test_fs))

        neg_upper = self.create_signal_unbounded(-3, [0, 1, 2, 3, 4], "forward")
        self.assertEqual((0, None), neg_upper.get_range(self.test_fs))
        self.assertEqual(5, neg_upper.get_period(self.test_fs))
