import unittest
from typing import cast
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from lukefi.metsi.data.vector_model import ReferenceTrees
from lukefi.metsi.sim.collected_data import CollectedData
import lukefi.metsi.domain.natural_processes.grow_metsi as gm
import lukefi.metsi.domain.natural_processes.grow_metsi as gmv
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.data.enums.internal import (LandUseCategory,
                                              SiteType,
                                              SoilPeatlandCategory
                                              )


def make_tree(
    stems=100.0,
    d=10.0,
    h=12.0,
    species_int=1,
    bio_age=30.0,
    bh_age=20.0,
    origin=None,   # None → NATURAL in predictor
):
    return SimpleNamespace(
        stems_per_ha=stems,
        breast_height_diameter=d,
        height=h,
        species=species_int,
        biological_age=bio_age,
        breast_height_age=bh_age,
        origin=origin,
    )


def make_stand(trees):
    # Pick valid enum values without knowing the exact names:
    mal_val = list(LandUseCategory)[0]
    mty_val = list(SiteType)[0]
    alr_val = list(SoilPeatlandCategory)[0]
    verl_val = list(gm.TaxClass)[0].value
    verlt_val = list(gm.TaxClassReduction)[0].value
    return ForestStand(
        year=2000,
        geo_location=(62.0, 25.0, 150.0, None),  # (Y, X, Z)
        degree_days=1100.0,
        sea_effect=0.0,
        lake_effect=0.0,
        land_use_category=mal_val,
        site_type_category=mty_val,
        soil_peatland_category=alr_val,
        tax_class=verl_val,
        tax_class_reduction=verlt_val,
        reference_trees_pre_vec=list(trees),
    )


def make_rtrees_soa(
    stems=(100.0,),
    d=(10.0,),
    h=(12.0,),
    species=(1,),
    bio_age=(30.0,),
    bh_age=(20.0,),
    origin=(None,),
) -> ReferenceTrees:
    n = len(stems)
    attr = {
        "identifier": ["" for _ in range(n)],
        "stems_per_ha": list(stems),
        "breast_height_diameter": list(d),
        "height": list(h),
        "species": list(species),
        "biological_age": list(bio_age),
        "breast_height_age": list(bh_age),
        "origin": list(origin),
    }
    return ReferenceTrees().vectorize(attr)


class TestMetsiGrowPredictorVec(unittest.TestCase):
    def test_spedom_uses_vectors_and_site_props_convert(self):
        # Patch species conversion to keep the test light-weight.
        with patch.object(gmv, "to_mg_species", side_effect=lambda s: gmv.Species.SPRUCE):
            # Two trees; only need species to influence spedom (dominant)
            rt = make_rtrees_soa(
                stems=(100.0, 80.0),
                d=(10.0, 8.0),
                h=(12.0, 9.0),
                species=(123, 999),
                bio_age=(30.0, 40.0),
                bh_age=(20.0, 30.0),
                origin=(None, None),
            )
            stand = make_stand([])  # site props + year from the common helper
            # Attach SoA trees
            stand.reference_trees = rt

            p = gmv.MetsiGrowPredictor(stand)

            # Dominant species should come from converted vectors
            self.assertEqual(p.spedom, gmv.Species.SPRUCE)

            # site/state properties should map to enums correctly (vectorized predictor)
            self.assertIsInstance(p.mal, gmv.LandUseCategoryVMI)
            self.assertEqual(p.mal, gmv.LandUseCategoryVMI(stand.land_use_category))
            self.assertIsInstance(p.mty, gmv.SiteTypeVMI)
            self.assertEqual(p.mty, gmv.SiteTypeVMI(stand.site_type_category))
            self.assertIsInstance(p.alr, gmv.SoilCategoryVMI)
            self.assertEqual(p.alr, gmv.SoilCategoryVMI(stand.soil_peatland_category))
            # verl may be optional; the AoS helper always provides a valid nonzero value
            self.assertIsInstance(p.verl, gmv.TaxClass)
            self.assertEqual(p.verl, gmv.TaxClass(stand.tax_class))
            self.assertIsInstance(p.verlt, gmv.TaxClassReduction)
            self.assertEqual(p.verlt, gmv.TaxClassReduction(stand.tax_class_reduction))

    def test_trees_spe_invalid_raises_vec(self):
        with patch.object(gmv, "to_mg_species", side_effect=ValueError("bad species")):
            rt = make_rtrees_soa(
                stems=(100.0,),
                d=(10.0,),
                h=(12.0,),
                species=(-42,),   # bad code -> conversion should raise
                bio_age=(30.0,),
                bh_age=(20.0,),
                origin=(None,),
            )
            stand = make_stand([])
            stand.reference_trees = rt

            p = gmv.MetsiGrowPredictor(stand)
            with self.assertRaises(ValueError):
                _ = p.trees_spe  # triggers conversion path with error


class TestGrowMetsiVecWrapper(unittest.TestCase):
    def test_grow_metsi_vec_applies_growth_and_prunes(self):
        # Two trees: the second will end with stems < 1 and be pruned
        rt = make_rtrees_soa(
            stems=(120.0, 0.8),
            d=(10.0, 8.0),
            h=(12.0, 9.0),
            species=(1, 2),
            bio_age=(30.0, 25.0),
            bh_age=(20.0, 18.0),
            origin=(None, None),
        )
        stand = make_stand([])
        stand.reference_trees = rt

        # Growth deltas returned by .evolve(step)
        growth = SimpleNamespace(
            trees_id=[0.5, -0.2],   # diameter deltas (cm)
            trees_ih=[1.0, 0.5],    # height deltas (m)
            trees_if=[-5.0, -0.2],  # stems/ha deltas
        )

        # Fake updater that applies new values to the SoA arrays and advances year
        def fake_update_stand_growth_vec(s, diameters, heights, stems, step):
            s.reference_trees.breast_height_diameter = np.asarray(diameters, dtype=float)
            s.reference_trees.height = np.asarray(heights, dtype=float)
            s.reference_trees.stems_per_ha = np.asarray(stems, dtype=float)
            s.year += step

        with (
            patch.object(gmv.MetsiGrowPredictor, "evolve", return_value=growth) as mock_evolve,
            patch.object(gmv, "update_stand_growth", side_effect=fake_update_stand_growth_vec) as mock_update,
            patch.object(gmv, "to_mg_species", side_effect=lambda s: gmv.Species.PINE),  # keep species simple
        ):
            out_stand, _ = gmv.grow_metsi((stand, CollectedData()), step=5)

            # evolve called with step=5
            mock_evolve.assert_called_once_with(step=5)
            self.assertTrue(mock_update.called)

            self.assertIsNotNone(out_stand.reference_trees)
            rt2 = cast(ReferenceTrees, out_stand.reference_trees)
            d = float(rt2.breast_height_diameter[0])
            h = float(rt2.height[0])
            s = float(rt2.stems_per_ha[0])

            self.assertAlmostEqual(d, 10.0 + 0.5, places=6)
            self.assertAlmostEqual(h, 12.0 + 1.0, places=6)
            self.assertAlmostEqual(s, 120.0 - 5.0, places=6)

            # tree 2 should be pruned (0.8 - 0.2 = 0.6 < 1.0)
            self.assertEqual(int(rt2.size), 1)

            # year advanced by step via our fake updater
            self.assertEqual(out_stand.year, 2005.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
