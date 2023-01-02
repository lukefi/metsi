from types import SimpleNamespace
import unittest
from domain.utils.collectives import CollectibleNDArray, autocollective, collect_all, compile, getvarfn
import numpy as np


class CollectivesTest(unittest.TestCase):

    def test_compile(self):
        f = compile("a+len(b)")
        getvar = getvarfn(a=1, b=[3,4])
        self.assertEqual(f(getvar), 1+2)

    def test_collectiblendarray(self):
        self.assertEqual(
            collect_all(
                {
                    "a": "xs",
                    "b": "xs[ys>0]"
                },
                getvar = getvarfn(
                    xs = np.array([1, 2, 3]).view(CollectibleNDArray),
                    ys = np.array([-1, 0, 1]).view(CollectibleNDArray)
                )
            ),
            {
                "a": 1+2+3,
                "b": 3
            }
        )

    def test_autocollective(self):
        globals = { "data": [SimpleNamespace(x=1, y=2), SimpleNamespace(x=-1, y=3)] }
        self.assertEqual(
            collect_all(
                {
                    "a": "data.y[data.x>0]",
                    "b": "data.x"
                },
                getvar = getvarfn(lambda name: autocollective(globals[name]))
            ),
            {
                "a": 2,
                "b": 0
            }
        )

    def test_undefined(self):
        f = compile("x")
        getvar = getvarfn()
        with self.assertRaises(NameError):
            f(getvar)
