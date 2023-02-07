from lukefi.metsi.data.model import TreeStratum
from lukefi.metsi.forestry.preprocessing import distributions
from tests.forestry import test_util


class TestDistributions(test_util.ConverterTestSuite):

    def test_reference_trees_from_height_distribution(self):
        """ Testing the generation of reference trees from sapling height distribution """
        fixture_values = [
            # species, mean_height, mean_diameter, stems_per_ha
            [1.0, 2.5, 1.8, 1350],
            [2.0, 1.4, 0.0, 1350],
            [2.0, 0.9, 0.0, 1350],
            [2.0, 1.25, 0.0, 1350],
            [1.0, 2.5, 1.8, 1350]
        ]
        tree_strata = [
            TreeStratum(
            species=value[0],
            mean_height=value[1],
            mean_diameter=value[2],
            stems_per_ha=value[3])
            for value in fixture_values
        ]
        assertions = \
        [
            (
                # TreeStratum, dominant_height, n_trees
                [tree_strata[0], 0.0, 10],  [(135, 1.788, 2.19),
                                            (135, 2.009, 2.34),
                                            (135, 2.112, 2.41),
                                            (135, 2.201, 2.47),
                                            (135, 2.275, 2.52),
                                            (135, 2.335, 2.56),
                                            (135, 2.394, 2.6),
                                            (135, 2.454, 2.64),
                                            (135, 2.529, 2.69),
                                            (135, 2.634, 2.76)]
            ),
            (
                [tree_strata[1], 0.0, 10],  [(135, 0.0, 1.22),
                                            (135, 0.664, 1.31),
                                            (135, 0.75, 1.35),
                                            (135, 0.814, 1.38),
                                            (135, 0.877, 1.41),
                                            (135, 0.918, 1.43),
                                            (135, 0.98, 1.46),
                                            (135, 1.022, 1.48),
                                            (135, 1.083, 1.51),
                                            (135, 1.164, 1.55)]
            ),
            (
                [tree_strata[2], 0.0, 10],  [(135, 0.0, 0.78),
                                            (135, 0.0, 0.84),
                                            (135, 0.0, 0.87),
                                            (135, 0.0, 0.89),
                                            (135, 0.0, 0.91),
                                            (135, 0.0, 0.92),
                                            (135, 0.0, 0.94),
                                            (135, 0.0, 0.95),
                                            (135, 0.0, 0.97),
                                            (135, 0.0, 1)]
            ),
            (
                [tree_strata[3], 0.0, 10],  [(135, 0.0, 1.09),
                                            (135, 0.0, 1.17),
                                            (135, 0.0, 1.21),
                                            (135, 0.0, 1.24),
                                            (135, 0.0, 1.26),
                                            (135,0.0, 1.28),
                                            (135, 0.643, 1.30),
                                            (135, 0.686, 1.32),
                                            (135, 0.75, 1.35),
                                            (135, 0.814, 1.38)]
            ),
            (
                [tree_strata[4], 0.0, 1],   [(1350, 1.80, 2.50)]
            )
        ]
        for i in assertions:
            tree_list = distributions.sapling_height_distribution(*i[0])
            asse = iter(i[1])
            for tree in tree_list:
                f = round(tree.stems_per_ha, 3)
                d = round(tree.breast_height_diameter, 3)
                h = round(tree.height, 3)
                result = (f, d, h)
                self.assertEqual(next(asse), result)
