from typing import List

from custom_types import Seconds
from signals.BufferSignal import BufferSignal
from signals.OffsetSignal import OffsetSignal
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

    def test_zero_offset_bounded(self):
        offset = self.create_signal(0, [0, 1, 2, 3, 4])
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4],
            offset.get_temporal(0, 5)
        )

        self.assertEqual(
            (0, 5),
            offset.get_range()
        )

    def test_offset_positive_bounded(self):
        offset = self.create_signal(4, [0, 1, 2, 3, 4])
        self.assertEqualsNumpy(
            [0, 0, 0, 0, 0, 1, 2, 3, 4],
            offset.get_temporal(0, 9)
        )
        self.assertEqual((4, 9), offset.get_range())

    def test_offset_negative_bounded(self):
        offset = self.create_signal(-4, [0, 1, 2, 3, 4])
        self.assertEqualsNumpy(
            [0, 1, 2, 3, 4, 0, 0, 0, 0],
            offset.get_temporal(-4, 5)
        )
        self.assertEqual((-4, 1), offset.get_range())
