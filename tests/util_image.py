# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unittests for objax.util.image."""

import io
import unittest
from typing import Tuple

import jax.numpy as jn
import numpy as np
from PIL import Image

import objax


class TestUtilImage(unittest.TestCase):
    def ndimarange(self, dims: Tuple[int, ...]):
        return np.arange(np.prod(dims), dtype=float).reshape(dims)

    def test_nchw(self):
        """Test nchw."""
        x = self.ndimarange((2, 3, 4, 5))
        self.assertEqual(objax.util.image.nchw(x).tolist(), x.transpose((0, 3, 1, 2)).tolist())
        self.assertEqual(objax.util.image.nchw(jn.array(x)).tolist(), x.transpose((0, 3, 1, 2)).tolist())
        x = self.ndimarange((2, 3, 4, 5, 6))
        self.assertEqual(objax.util.image.nchw(x).tolist(), x.transpose((0, 1, 4, 2, 3)).tolist())
        self.assertEqual(objax.util.image.nchw(jn.array(x)).tolist(), x.transpose((0, 1, 4, 2, 3)).tolist())

    def test_nhwc(self):
        """Test nhwc."""
        x = self.ndimarange((2, 3, 4, 5))
        self.assertEqual(objax.util.image.nhwc(x).tolist(), x.transpose((0, 2, 3, 1)).tolist())
        self.assertEqual(objax.util.image.nhwc(jn.array(x)).tolist(), x.transpose((0, 2, 3, 1)).tolist())
        x = self.ndimarange((2, 3, 4, 5, 6))
        self.assertEqual(objax.util.image.nhwc(x).tolist(), x.transpose((0, 1, 3, 4, 2)).tolist())
        self.assertEqual(objax.util.image.nhwc(jn.array(x)).tolist(), x.transpose((0, 1, 3, 4, 2)).tolist())

    def test_normalize(self):
        """Test normalize methods."""
        x = np.arange(256)
        y = objax.util.image.normalize_to_unit_float(x)
        self.assertEqual((x / 128 - (1 - 1 / 256)).tolist(), y.tolist())
        self.assertEqual(y.tolist(), y.clip(-1, 1).tolist())
        z = objax.util.image.normalize_to_uint8(y)
        self.assertEqual(x.tolist(), z.tolist())
        z = objax.util.image.normalize_to_uint8(y + 1 / 128)
        self.assertEqual((x + 1).clip(0, 255).tolist(), z.tolist())
        z = objax.util.image.normalize_to_uint8(y - 1 / 128)
        self.assertEqual((x - 1).clip(0, 255).tolist(), z.tolist())

    def test_to_png(self):
        """Test to_png."""
        x = np.zeros((3, 32, 32), np.float) + 1 / 255
        x[:, :12, :12] = 1
        x[:, -12:, -12:] = -1
        y = objax.util.image.to_png(x)
        self.assertEqual(y, b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x02\x00\x00\x00\xfc'
                            b'\x18\xed\xa3\x00\x00\x00FIDATx\x9cc\xfc\xff\xff?\x03!\xd0\xd8\xd8HP\r.\xc0D\xb6\xceQ'
                            b'\x0bF-\x18\xb5`\x04Y\xc0BI9C\x0c\x18\xfaA4j\xc1\x08\xb0\x80\x85\x12\xcd\r\r\r\x04\xd5'
                            b'\x0c\xfd \x1a\xb5`\xd4\x82Q\x0b\xe8`\x01\x00\xe3\xf1\x07\xc7\x82\x83p\xa5\x00\x00\x00\x00'
                            b'IEND\xaeB`\x82')
        z = np.array(Image.open(io.BytesIO(y)))
        z = (z.transpose((2, 0, 1)) - 127.5) / 127.5
        self.assertEqual(x.tolist(), z.tolist())


if __name__ == '__main__':
    unittest.main()
