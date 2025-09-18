import unittest

import numpy as np
import numpy.typing as npt

from lukefi.metsi.data.vector_model import VectorData

DUMMY_DTYPES: dict[str, npt.DTypeLike] = {
    "x": np.int32,
    "y": np.int64,
    "z": np.float64
}


class DummyVectors(VectorData):
    x: npt.NDArray[np.int32]
    y: npt.NDArray[np.int64]
    z: npt.NDArray[np.float64]


class VectorModelTest(unittest.TestCase):

    def setUp(self):
        self.vector_data = DummyVectors(DUMMY_DTYPES)
        self.vector_data.x = np.array([], np.int32)
        self.vector_data.y = np.array([], np.int64)
        self.vector_data.z = np.array([], np.float64)

    def test_create(self):
        self.vector_data.create({"x": 1, "y": 2, "z": 3.0})

        self.assertEqual(len(self.vector_data.x), 1)
        self.assertEqual(len(self.vector_data.y), 1)
        self.assertEqual(len(self.vector_data.z), 1)

        self.assertEqual(self.vector_data.x[0], 1)
        self.assertEqual(self.vector_data.y[0], 2)
        self.assertEqual(self.vector_data.z[0], 3.0)

        self.vector_data.create({"x": 4, "y": 5, "z": 6.0})

        self.assertEqual(len(self.vector_data.x), 2)
        self.assertEqual(len(self.vector_data.y), 2)
        self.assertEqual(len(self.vector_data.z), 2)

        self.assertEqual(self.vector_data.x[0], 1)
        self.assertEqual(self.vector_data.y[0], 2)
        self.assertEqual(self.vector_data.z[0], 3.0)

        self.assertEqual(self.vector_data.x[1], 4)
        self.assertEqual(self.vector_data.y[1], 5)
        self.assertEqual(self.vector_data.z[1], 6.0)

        self.vector_data.create({"x": 7}, 1)

        self.assertEqual(len(self.vector_data.x), 3)
        self.assertEqual(len(self.vector_data.y), 3)
        self.assertEqual(len(self.vector_data.z), 3)

        self.assertEqual(self.vector_data.x[0], 1)
        self.assertEqual(self.vector_data.y[0], 2)
        self.assertEqual(self.vector_data.z[0], 3.0)

        self.assertEqual(self.vector_data.x[1], 7)
        self.assertEqual(self.vector_data.y[1], 0)
        self.assertEqual(self.vector_data.z[1], 0.0)

        self.assertEqual(self.vector_data.x[2], 4)
        self.assertEqual(self.vector_data.y[2], 5)
        self.assertEqual(self.vector_data.z[2], 6.0)

    def test_create_multiple(self):
        self.vector_data.create([{"x": 1, "y": 2, "z": 3.0}, {"x": 4, "y": 5, "z": 6.0}, {"x": 7, "y": 8, "z": 9.0}])
        self.vector_data.create([{"x": 10, "y": 11, "z": 12.0}, {"x": 13, "y": 14,
                                "z": 15.0}, {"x": 16, "y": 17, "z": 18.0}], index=[1, 2, 3])

        self.assertEqual(len(self.vector_data.x), 6)
        self.assertEqual(len(self.vector_data.y), 6)
        self.assertEqual(len(self.vector_data.z), 6)

        self.assertEqual(self.vector_data.x[0], 1)
        self.assertEqual(self.vector_data.y[0], 2)
        self.assertEqual(self.vector_data.z[0], 3.0)

        self.assertEqual(self.vector_data.x[1], 10)
        self.assertEqual(self.vector_data.y[1], 11)
        self.assertEqual(self.vector_data.z[1], 12.0)

        self.assertEqual(self.vector_data.x[2], 4)
        self.assertEqual(self.vector_data.y[2], 5)
        self.assertEqual(self.vector_data.z[2], 6.0)

        self.assertEqual(self.vector_data.x[3], 13)
        self.assertEqual(self.vector_data.y[3], 14)
        self.assertEqual(self.vector_data.z[3], 15.0)

        self.assertEqual(self.vector_data.x[4], 7)
        self.assertEqual(self.vector_data.y[4], 8)
        self.assertEqual(self.vector_data.z[4], 9.0)

        self.assertEqual(self.vector_data.x[5], 16)
        self.assertEqual(self.vector_data.y[5], 17)
        self.assertEqual(self.vector_data.z[5], 18.0)

    def test_read(self):
        self.vector_data.create([{"x": 1, "y": 2, "z": 3.0}, {"x": 4, "y": 5, "z": 6.0}])
        self.vector_data.create({"x": 7}, 1)

        self.assertDictEqual(self.vector_data.read(0), {"x": 1, "y": 2, "z": 3.0})
        self.assertDictEqual(self.vector_data.read(2), {"x": 4, "y": 5, "z": 6.0})
        self.assertEqual(self.vector_data.read(1)["x"], 7)
        self.assertEqual(self.vector_data.read(1)["y"], 0)
        self.assertEqual(self.vector_data.read(1)["z"], 0.0)

    def test_update(self):
        self.vector_data.create({"x": 1, "y": 2, "z": 3.0})
        self.vector_data.create({"x": 4, "y": 5, "z": 6.0})
        self.vector_data.create({"x": 7}, 1)

        self.vector_data.update({"x": 8, "z": 9.0}, 2)

        self.assertEqual(len(self.vector_data.x), 3)
        self.assertEqual(len(self.vector_data.y), 3)
        self.assertEqual(len(self.vector_data.z), 3)

        self.assertEqual(self.vector_data.x[0], 1)
        self.assertEqual(self.vector_data.y[0], 2)
        self.assertEqual(self.vector_data.z[0], 3.0)

        self.assertEqual(self.vector_data.x[1], 7)
        self.assertEqual(self.vector_data.y[1], 0)
        self.assertEqual(self.vector_data.read(1)["z"], 0.0)

        self.assertEqual(self.vector_data.x[2], 8)
        self.assertEqual(self.vector_data.y[2], 5)
        self.assertEqual(self.vector_data.z[2], 9.0)

    def test_delete(self):
        self.vector_data.create({"x": 1, "y": 2, "z": 3.0})
        self.vector_data.create({"x": 4, "y": 5, "z": 6.0})
        self.vector_data.create({"x": 7}, 1)

        self.vector_data.delete(1)

        self.assertEqual(len(self.vector_data.x), 2)
        self.assertEqual(len(self.vector_data.y), 2)
        self.assertEqual(len(self.vector_data.z), 2)

        self.assertEqual(self.vector_data.x[0], 1)
        self.assertEqual(self.vector_data.y[0], 2)
        self.assertEqual(self.vector_data.z[0], 3.0)

        self.assertEqual(self.vector_data.x[1], 4)
        self.assertEqual(self.vector_data.y[1], 5)
        self.assertEqual(self.vector_data.z[1], 6.0)

    def test_finalize_and_update(self):
        self.vector_data.create([{"x": 1, "y": 2, "z": 3.0}, {"x": 4, "y": 5, "z": 6.0}, {"x": 7, "y": 8, "z": 9.0}])

        vector_data_copy = self.vector_data.finalize()

        self.assertEqual(len(self.vector_data.x), 3)
        self.assertEqual(len(self.vector_data.y), 3)
        self.assertEqual(len(self.vector_data.z), 3)

        self.assertEqual(vector_data_copy.x[0], 1)
        self.assertEqual(vector_data_copy.y[0], 2)
        self.assertEqual(vector_data_copy.z[0], 3.0)

        self.assertEqual(vector_data_copy.x[1], 4)
        self.assertEqual(vector_data_copy.y[1], 5)
        self.assertEqual(vector_data_copy.z[1], 6.0)

        self.assertEqual(vector_data_copy.x[2], 7)
        self.assertEqual(vector_data_copy.y[2], 8)
        self.assertEqual(vector_data_copy.z[2], 9.0)

        vector_data_copy.update({"x": 10}, 0)
        vector_data_copy.update({"z": 11.5}, 1)

        self.assertEqual(vector_data_copy.x[0], 10)
        self.assertEqual(vector_data_copy.y[0], 2)
        self.assertEqual(vector_data_copy.z[0], 3.0)

        self.assertEqual(vector_data_copy.x[1], 4)
        self.assertEqual(vector_data_copy.y[1], 5)
        self.assertEqual(vector_data_copy.z[1], 11.5)

        self.assertEqual(vector_data_copy.x[2], 7)
        self.assertEqual(vector_data_copy.y[2], 8)
        self.assertEqual(vector_data_copy.z[2], 9.0)

        self.assertEqual(self.vector_data.x[0], 1)
        self.assertEqual(self.vector_data.y[0], 2)
        self.assertEqual(self.vector_data.z[0], 3.0)

        self.assertEqual(self.vector_data.x[1], 4)
        self.assertEqual(self.vector_data.y[1], 5)
        self.assertEqual(self.vector_data.z[1], 6.0)

        self.assertEqual(self.vector_data.x[2], 7)
        self.assertEqual(self.vector_data.y[2], 8)
        self.assertEqual(self.vector_data.z[2], 9.0)

    def test_finalize_and_create(self):
        self.vector_data.create([{"x": 1, "y": 2, "z": 3.0}, {"x": 4, "y": 5, "z": 6.0}, {"x": 7, "y": 8, "z": 9.0}])
        vector_data_copy = self.vector_data.finalize()
        vector_data_copy.create({"x": 12, "y": 13, "z": 14.0})

        self.assertEqual(len(self.vector_data.x), 3)
        self.assertEqual(len(self.vector_data.y), 3)
        self.assertEqual(len(self.vector_data.z), 3)

        self.assertEqual(len(vector_data_copy.x), 4)
        self.assertEqual(len(vector_data_copy.y), 4)
        self.assertEqual(len(vector_data_copy.z), 4)

        self.assertEqual(vector_data_copy.x[0], 1)
        self.assertEqual(vector_data_copy.y[0], 2)
        self.assertEqual(vector_data_copy.z[0], 3.0)

        self.assertEqual(vector_data_copy.x[1], 4)
        self.assertEqual(vector_data_copy.y[1], 5)
        self.assertEqual(vector_data_copy.z[1], 6.0)

        self.assertEqual(vector_data_copy.x[2], 7)
        self.assertEqual(vector_data_copy.y[2], 8)
        self.assertEqual(vector_data_copy.z[2], 9.0)

        self.assertEqual(vector_data_copy.x[3], 12)
        self.assertEqual(vector_data_copy.y[3], 13)
        self.assertEqual(vector_data_copy.z[3], 14.0)

        self.assertEqual(self.vector_data.x[0], 1)
        self.assertEqual(self.vector_data.y[0], 2)
        self.assertEqual(self.vector_data.z[0], 3.0)

        self.assertEqual(self.vector_data.x[1], 4)
        self.assertEqual(self.vector_data.y[1], 5)
        self.assertEqual(self.vector_data.z[1], 6.0)

        self.assertEqual(self.vector_data.x[2], 7)
        self.assertEqual(self.vector_data.y[2], 8)
        self.assertEqual(self.vector_data.z[2], 9.0)
