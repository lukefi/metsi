import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from cffi import FFI
import lukefi.metsi.domain.natural_processes.motti_dll_wrapper as pymd
import lukefi.metsi.domain.natural_processes.grow_motti_dll as gm_dll


# ----------- helpers (mirroring grow_metsi_test style) -----------

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
    return SimpleNamespace(
        year=2000.0,
        geo_location=(62.0, 25.0, 150.0),  # (Y, X, Z)
        lake_effect=0.0,
        sea_effect=0.0,
        land_use_category=1,
        site_type_category=3,
        soil_peatland_category=1,
        tax_class=1,
        tax_class_reduction=0,
        reference_trees=list(trees),
    )


# ----------- Low-level wrapper helper tests (no real DLL needed) -----------

class TestMottiDLLHelpers(unittest.TestCase):
    def test_auto_euref_km_validations(self):
        y, x = gm_dll.auto_euref_km(6900000.0, 3400000.0)
        self.assertEqual((y, x), (6900.0, 3400.0))
        y2, x2 = gm_dll.auto_euref_km(6900.0, 3400.0)
        self.assertEqual((y2, x2), (6.9000, 3.4000))
        with self.assertRaises(ValueError):
            gm_dll.auto_euref_km(62.0, 25.0)

    def test_maybe_chdir_context_manager(self):
        orig = Path.cwd()
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            with pymd.Motti4DLL.maybe_chdir(td_path):
                self.assertEqual(Path.cwd(), td_path)
            self.assertEqual(Path.cwd(), orig)

    def test_convert_fallbacks_without_real_lib(self):
        dummy = Path("dummy_lib.so").resolve()
        key = str(dummy).lower()
        ffi = FFI()
        pymd.Motti4DLL.set_lib_cache(key, (ffi, SimpleNamespace()))
        dll = pymd.Motti4DLL(dummy)

        # species mapping fallback: 7→8, 8→9; else unchanged
        self.assertEqual(gm_dll.species_to_motti(7), 6)
        self.assertEqual(gm_dll.species_to_motti(8), 8)
        self.assertEqual(gm_dll.species_to_motti(3), 3)

        # site index cap at 6
        self.assertEqual(dll.convert_site_index(10), 6)
        self.assertEqual(dll.convert_site_index(5), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
