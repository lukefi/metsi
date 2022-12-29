import io
from types import SimpleNamespace
from typing import OrderedDict
import unittest
from app.export_handlers.j import j_xda, j_cda
from sim.core_types import CollectedData, OperationPayload


class TestExport(unittest.TestCase):

    def test_j_out(self):
        decl = {
            "cvariables": [ "a", "b", ],
            "xvariables": [ "x", "y[0,5]", "z[10]" ]
        }
        data = {
            "1": [
                OperationPayload(
                    computational_unit = SimpleNamespace(a=1, b=2),
                    collected_data = CollectedData(
                        operation_results = {
                            "report_collectives": OrderedDict({
                                0: { "x": 1, "y": 2, "z": 3 },
                                5: { "x": 4, "y": 5, "z": 6 },
                                10: { "x": 7, "y": 8, "z": 9 }
                            })
                        }
                    )
                )
            ],
            "2": [
                OperationPayload(
                    computational_unit = SimpleNamespace(a=-1, b=-2),
                    collected_data = CollectedData(
                        operation_results = {
                            "report_collectives": OrderedDict({
                                0: { "x": 10, "y": 20, "z": 30 },
                                5: { "x": 40, "y": 50, "z": 60 },
                                10: { "x": 70, "y": 80, "z": 90 }
                            })
                        }
                    )
                ),
                OperationPayload(
                    computational_unit = SimpleNamespace(a=-1, b=-2),
                    collected_data = CollectedData(
                        operation_results = {
                            "report_collectives": OrderedDict({
                                0: { "x": -1, "y": -2, "z": -3 },
                                5: { "x": 4, "y": 5, "z": 6 },
                                10: { "x": 7, "y": 8, "z": 9 }
                            })
                        }
                    )
                )
            ]
        }
        cda = io.StringIO()
        j_cda(out=cda, data=data, cvariables=decl["cvariables"])
        self.assertEqual(
            cda.getvalue(),
            (
                "1\t1\t2\n"
                "2\t-1\t-2\n"
            )
        )
        xda = io.StringIO()
        j_xda(out=xda,data=data, xvariables=decl["xvariables"])
        self.assertEqual(
            xda.getvalue(),
            (
                "1\t4\t7\t2\t5\t9\n"
                "10\t40\t70\t20\t50\t90\n"
                "-1\t4\t7\t-2\t5\t9\n"
            )
        )
