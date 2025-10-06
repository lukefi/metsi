import unittest
from lukefi.metsi.domain.utils.filter import applyfilter
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeSpecies, TreeStratum

from lukefi.metsi.domain.pre_ops import preproc_filter

class FilterTest(unittest.TestCase):

    def test_filter_stands(self):
        s900  = ForestStand(identifier="1", degree_days=900)
        s1000 = ForestStand(identifier="2", degree_days=1000)
        s1100 = ForestStand(identifier="3", degree_days=1100)
        self.assertEqual(
            applyfilter([s900, s1000, s1100], "select stands", "degree_days > 1050"),
            [s1100]
        )
        self.assertEqual(
            applyfilter([s900, s1000, s1100], "remove stands", "degree_days > 1050"),
            [s900, s1000]
        )

    def test_filter_lists(self):
        t1 = ReferenceTree(identifier="t-1", species=TreeSpecies.PINE, breast_height_diameter=0, height=0.7)
        t2 = ReferenceTree(identifier="t-2", species=TreeSpecies.SPRUCE, breast_height_diameter=0, height=0.6)
        t3 = ReferenceTree(identifier="t-3", species=TreeSpecies.SILVER_BIRCH, breast_height_diameter=20, height=25)
        t4 = ReferenceTree(identifier="t-4", species=TreeSpecies.GREY_ALDER, breast_height_diameter=10, height=15)
        t5 = ReferenceTree(identifier="t-5", species=TreeSpecies.ASPEN, breast_height_diameter=15, height=18)
        s1 = TreeStratum(identifier="s-1", species=TreeSpecies.PINE)
        s2 = TreeStratum(identifier="s-2", species=TreeSpecies.SPRUCE)
        stand1 = ForestStand(identifier="S-1", reference_trees_pre_vec = [t1, t2, t3], tree_strata_pre_vec = [s1, s2])
        stand2 = ForestStand(identifier="S-2", reference_trees_pre_vec = [t4, t5], tree_strata_pre_vec = [])
        applyfilter([stand1, stand2], "remove trees", "height < 1.3 and species == 1")
        self.assertEqual(stand1.reference_trees_pre_vec, [t2, t3])
        self.assertEqual(stand2.reference_trees_pre_vec, [t4, t5])
        applyfilter([stand1, stand2], "select trees", "height > 20")
        self.assertEqual(stand1.reference_trees_pre_vec, [t3])
        self.assertEqual(stand2.reference_trees_pre_vec, [])
        applyfilter([stand1, stand2], "select strata", "species == 2")
        self.assertEqual(stand1.tree_strata_pre_vec, [s2])
        self.assertEqual(stand2.tree_strata_pre_vec, [])

    def test_filter_named(self):
        s1 = ForestStand(identifier="1")
        s2 = ForestStand(identifier="2")
        s3 = ForestStand(identifier="3")
        self.assertEqual(
            applyfilter(
                [s1, s2, s3],
                "select",
                "first or third",
                named = {
                    "first":  "identifier == '1'",
                    "second": "identifier == '2'",
                    "third":  "identifier == '3'"
                }
            ),
            [s1, s3]
        )

    def test_reject_invalid_command(self):
        with self.assertRaisesRegex(ValueError, "filter syntax error"):
            applyfilter([], "? ? ?", "1")
        with self.assertRaisesRegex(ValueError, "invalid filter verb"):
            applyfilter([], "choose", "1")
        with self.assertRaisesRegex(ValueError, "invalid filter object"):
            applyfilter([], "select something", "1")

    def test_preproc_filter(self):
        t1 = ReferenceTree(identifier="1")
        t2 = ReferenceTree(identifier="2")
        t3 = ReferenceTree(identifier="3")
        t4 = ReferenceTree(identifier="4")
        s1 = ForestStand(identifier="1", reference_trees_pre_vec=[t1, t2, t3])
        s2 = ForestStand(identifier="2", reference_trees_pre_vec=[t4])
        stands = preproc_filter([s1, s2], **{
            "named": {
                "four":  "identifier == '4'",
                "empty": "not reference_trees_pre_vec"
            },
            "remove trees": "identifier == '3' or four",
            "select": "not empty"
        })
        self.assertEqual(stands, [s1])
        self.assertEqual(s1.reference_trees_pre_vec, [t1, t2])
        self.assertEqual(s2.reference_trees_pre_vec, [])
