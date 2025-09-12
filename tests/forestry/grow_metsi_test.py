import unittest
from typing import cast
from types import SimpleNamespace
from unittest.mock import patch
import lukefi.metsi.domain.natural_processes.grow_metsi as mg
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
    mal_val  = list(LandUseCategory)[0]
    mty_val  = list(SiteType)[0]
    alr_val  = list(SoilPeatlandCategory)[0]
    verl_val = list(mg.TaxClass)[0].value
    verlt_val= list(mg.TaxClassReduction)[0].value
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
        reference_trees=list(trees),
    )


class TestMetsiGrowPredictor(unittest.TestCase):
    def test_spedom_uses_first_tree_and_site_props_convert(self):
        # Patch species conversion to keep the test light-weight.
        with patch.object(mg, "to_mg_species", side_effect=lambda s: mg.Species.SPRUCE):
            t1 = make_tree(species_int=123)
            t2 = make_tree(species_int=999)
            stand = make_stand([t1, t2])
            p = mg.MetsiGrowPredictor(stand)

            # spedom should be computed from the *first* reference tree
            self.assertEqual(p.spedom, mg.Species.SPRUCE)

            # site/state properties should map to enums correctly
            self.assertIsInstance(p.mal, mg.LandUseCategoryVMI)
            self.assertEqual(p.mal, mg.LandUseCategoryVMI(stand.land_use_category))
            self.assertIsInstance(p.mty, mg.SiteTypeVMI)
            self.assertEqual(p.mty, mg.SiteTypeVMI(stand.site_type_category))
            self.assertIsInstance(p.alr, mg.SoilCategoryVMI)
            self.assertEqual(p.alr, mg.SoilCategoryVMI(stand.soil_peatland_category))
            self.assertIsInstance(p.verl, mg.TaxClass)
            self.assertEqual(p.verl, mg.TaxClass(stand.tax_class))
            self.assertIsInstance(p.verlt, mg.TaxClassReduction)
            self.assertEqual(p.verlt, mg.TaxClassReduction(stand.tax_class_reduction))

    def test_trees_spe_invalid_raises_and_is_logged(self):
        # Make spe2metsi raise to verify error propagation
        with patch.object(mg, "to_mg_species", side_effect=ValueError("bad species")):
            t_bad = make_tree(species_int=-42)
            stand = make_stand([t_bad])
            p = mg.MetsiGrowPredictor(stand)
            with self.assertRaises(ValueError):
                _ = p.trees_spe  # triggers conversion path with error


class TestGrowMetsiWrapper(unittest.TestCase):
    def test_grow_metsi_applies_growth_and_prunes(self):
        # Two trees: the second will end with stems < 1 and be pruned
        t1 = make_tree(stems=120.0, d=10.0, h=12.0, species_int=1)
        t2 = make_tree(stems=0.8,  d=8.0,  h=9.0,  species_int=2)
        stand = make_stand([t1, t2])

        # Growth deltas returned by .evolve(step)
        growth = SimpleNamespace(
            trees_id=[0.5, -0.2],   # diameter deltas (cm)
            trees_ih=[1.0, 0.5],    # height deltas (m)
            trees_if=[-5.0, -0.2],  # stems/ha deltas
        )

        # Fake updater that applies the new values to the same tree objects
        def fake_update_stand_growth(s, diameters, heights, stems, step):
            for tt, d, h, f in zip(s.reference_trees, diameters, heights, stems):
                tt.breast_height_diameter = d
                tt.height = h
                tt.stems_per_ha = f
            s.year += step

        with (
            patch.object(mg.MetsiGrowPredictor, "evolve", return_value=growth) as mock_evolve,
            patch.object(mg, "update_stand_growth", side_effect=fake_update_stand_growth) as mock_update,
            patch.object(mg, "to_mg_species", side_effect=lambda s: mg.Species.PINE),  # keep species simple
        ):
            out_stand, _ = mg.grow_metsi((stand, None), step=5)

            # evolve called with step=5
            mock_evolve.assert_called_once_with(step=5)
            self.assertTrue(mock_update.called)

            d = out_stand.reference_trees[0].breast_height_diameter
            h = out_stand.reference_trees[0].height
            s = out_stand.reference_trees[0].stems_per_ha

            self.assertIsNotNone(d)
            self.assertIsNotNone(h)
            self.assertIsNotNone(s)

            self.assertAlmostEqual(cast(float, d), 10.0 + 0.5, places=6)
            self.assertAlmostEqual(cast(float, h), 12.0 + 1.0, places=6)
            self.assertAlmostEqual(cast(float, s), 120.0 - 5.0, places=6)

            # tree 2 should be pruned (0.8 - 0.2 = 0.6 < 1.0)
            self.assertEqual(len(out_stand.reference_trees), 1)

            # year advanced by step via our fake updater
            self.assertEqual(out_stand.year, 2005.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
