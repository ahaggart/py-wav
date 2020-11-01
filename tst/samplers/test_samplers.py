import unittest
from unittest import mock

from samplers.DilatedSampler import DilatedSampler
from samplers.OffsetSampler import OffsetSampler
from samplers.Sampler import Sampler, RootSampler


class SamplerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fs = 4
        self.test_source = mock.Mock()
        self.root_sampler = RootSampler(self.fs)

    def test_sampling(self):
        sampler = Sampler(self.root_sampler)
        sampler.sample(self.test_source, self.fs, 0, 5)
        self.test_source.get_buffer.assert_called_once_with(self.fs, 0, 5)

    def test_sampling_offset(self):
        sampler = Sampler(self.root_sampler)
        sampler.sample(self.test_source, self.fs, 1, 10)
        self.test_source.get_buffer.assert_called_once_with(self.fs, 4, 14)

    def test_dilated_sampling(self):
        sampler = DilatedSampler(0.5, self.root_sampler)
        sampler.sample(self.test_source, self.fs, 2, 5)
        self.test_source.get_buffer.assert_called_once_with(self.fs, 4, 9)

    def test_offset_sampling(self):
        sampler = OffsetSampler(1, self.root_sampler)
        sampler.sample(self.test_source, self.fs, 0, 5)
        self.test_source.get_buffer.assert_called_once_with(self.fs, 4, 9)


class CompoundSamplerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.test_source = mock.Mock()
        self.root_fs = 1
        self.root_sampler = RootSampler(self.root_fs)

    def test_offset_dilated(self):
        """Sample a non-dilated source into a dilated, offset space.

        We expect the sampling to occur at the sampler's fs, with a start and
        end offset by the number of frames in the sampler's offset.
        """
        fs = 2
        sampler = DilatedSampler(0.5, OffsetSampler(3, self.root_sampler))
        sampler.sample(self.test_source, fs, 2, 6)
        self.test_source.get_buffer.assert_called_once_with(fs, 8, 14)

    def test_dilated_offset_dilated(self):
        fs = 4
        sampler = DilatedSampler(0.5, OffsetSampler(2, DilatedSampler(0.5, self.root_sampler)))
        sampler.sample(self.test_source, fs, 2, 8)
        self.test_source.get_buffer.assert_called_once_with(fs, 6, 14)

