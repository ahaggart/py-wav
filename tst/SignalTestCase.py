from unittest import TestCase

import numpy as np

from SignalData import SignalData


class SignalTestCase(TestCase):
    def assertEqualsNumpy(self, a1, a2, msg=None):
        self.assertTrue(
            np.array_equal(a1, a2),
            msg=f"{a1} != {a2}" + (msg if msg is not None else ""),
        )

    @staticmethod
    def get_signal_data(data: dict, *, resolved_refs=None) -> SignalData:
        signal_data = SignalData({"uuid": "test", "type": "test", **data})
        signal_data.set_refs(resolved_refs if resolved_refs is not None else {})
        return signal_data
