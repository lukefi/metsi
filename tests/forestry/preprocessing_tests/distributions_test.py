from lukefi.metsi.data.model import TreeStratum, ReferenceTree
from lukefi.metsi.forestry.preprocessing import distributions
from tests.forestry import test_util


class TestDistributions(test_util.ConverterTestSuite):
    def test_weibull_coeffs(self):
        assertions = [
            ([1.0, 1.0, 0.0], (0.0, 1.1931032411956006, 2.075882078133891)),
            ([1.0, 1.0, 1.0], (1.0, 0.0, 2.075882078133891)),
            ([28.0, 27.0, None], (13.436882429476194, 16.133339870229843, 3.5793748463876014)),
        ]
        self.run_with_test_assertions(assertions, distributions.weibull_coeffs)

    def test_weibull(self):
        """
        Testing the generation of reference trees from weibull distribution

        Input values:
            number of trees, mean diameter, basal_area, mean height, (optional) minimum diameter
        Ouput values:
            List length is equal to the number of of trees in input
            (stems per hectare, diameter)
         """
        assertions = \
        [
                (
                    [3, 28.0, 27.0, 1.3, 1.0],  [(397.6019036828729, 8.637987634768177),
                                                 (344.873773814757, 23.91396290430453),
                                                 (76.10255713402002, 39.189938173840886)]
                ),
                (
                    [3, 9.0, 11.0, 7.0, 0.0],   [(3599.7420367640484, 3.292627801937575),
                                                 (782.0402495299719, 9.877883405812725),
                                                 (91.22247720267801, 16.463139009687875)]
                ),
                (
                    [10, 28.0, 27.0, 22.0, None],   [(1.9357767362985978, 14.67280367311326),
                                                     (15.418294669238696, 17.144646160387396),
                                                     (40.759532527459875, 19.61648864766153),
                                                     (69.83978839638895, 22.088331134935665),
                                                     (91.5190988847183, 24.5601736222098),
                                                     (95.55426828265567, 27.032016109483934),
                                                     (79.15401349329443, 29.503858596758068),
                                                     (50.70111416700932, 31.975701084032202),
                                                     (24.176363582009767, 34.44754357130633),
                                                     (10.717763528467435, 36.919386058580464)]
                )
            ]
        for i in assertions:
            tree_list = distributions.weibull(*i[0])
            asse = iter(i[1])
            for tree in tree_list:
                result = (tree.stems_per_ha, tree.breast_height_diameter)
                self.assertEqual(next(asse), result)

    def test_trees_from_simple_height_distribution(self):
        fixture = TreeStratum()
        fixture.mean_diameter = 28.0
        fixture.stems_per_ha = 170.0
        fixture.mean_height = 22.0
        n_trees = 10
        result = distributions.simple_height_distribution(fixture, n_trees)
        self.assertEqual(10, len(result))
        self.assertEqual(17, result[0].stems_per_ha)
        self.assertEqual(17, result[1].stems_per_ha)
        self.assertEqual(28.0, result[0].breast_height_diameter)
        self.assertEqual(28.0, result[1].breast_height_diameter)
        self.assertEqual(22.0, result[0].height)
        self.assertEqual(22.0, result[1].height)

    def test_diameter_model_valkonen(self):
        result = distributions.diameter_model_valkonen(height_rt=10.0)
        self.assertEqual(result, 13.961394503710512)

    def test_diameter_model_siipilehto(self):
        result = distributions.diameter_model_siipilehto(height_rt=10.0, height=12.0, diameter=9.0, dominant_height=1.1)
        self.assertEqual(result, 10.94882228311327)

    def test_predict_sapling_diameters(self):
        assertions = [
            # height and diameter tuples
            (10.0, 11.553041860956098),
            (10.0, 13.961394503710512),
            (10.0, 13.961394503710512),
            (10.0, 0.0),
            (1.0, 0.0)
        ]
        hs = [10.0, 10.0, 10.0, 10.0, 1.0]
        ds = [8.0, 8.0, 8.0, 8.0, 8.0]
        reference_trees = [
            [ ReferenceTree(
                height=h,
                breast_height_diameter=d) ]
            for h, d in zip(hs, ds)
        ]
        avghs = [20.0, 1.3, 1.2, 1.2, 999.0]
        avgds = [18.0, 0.0, 0.0, 10.0, 999.0]
        strata = [
            TreeStratum(
                mean_height=h,
                mean_diameter=d)
            for h, d in zip(avghs, avgds)
        ]
        for rts, st, ass in zip(reference_trees, strata, assertions):
            result = distributions.predict_sapling_diameters(
                rts,
                height=st.mean_height,
                diameter=st.mean_diameter,
                dominant_height=1.1)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].height, ass[0])
            self.assertEqual(result[0].breast_height_diameter, ass[1])

    def test_weibull_sapling(self):
        assertions = [
            7.84,
            8.72,
            9.19,
            9.54,
            9.84,
            10.11,
            10.37,
            10.64,
            10.95,
            11.42
        ]
        result = distributions.weibull_sapling(
            height=10.0,
            stem_count=99.0,
            dominant_height=1.1,
            n_trees=10)
        self.assertEqual(len(result), 10)
        for res, asse in zip(result, assertions):
            self.assertEqual(res.sapling, True)
            self.assertEqual(res.stems_per_ha, 9.9)
            self.assertEqual(res.height, asse)
