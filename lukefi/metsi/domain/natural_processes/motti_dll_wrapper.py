from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple, Optional, Dict, Any, cast
import os
from contextlib import contextmanager

from cffi import FFI


@dataclass
class GrowthDeltas:
    tree_ids: List[int]   # IDs of trees that survived in the DLL after growth
    trees_id: List[float]   # diameter increments (xd)
    trees_ih: List[float]   # height increments (xh)
    trees_if: List[float]   # stems/ha delta (Δf)

@contextmanager
def _maybe_chdir(tmp_dir: Optional[Path] = None):
    if tmp_dir is None:
        yield
        return
    prev = Path.cwd()
    try:
        os.chdir(str(tmp_dir))
        yield
    finally:
        os.chdir(str(prev))


class Motti4DLL:
    # Class-level caches to avoid reloading the DLL (and re-adding search dirs)
    _LIB_CACHE = {}          # key: resolved dll path (str) -> (ffi, lib)
    _DLL_DIR_HANDLES = {}    # key: dir path (str) -> handle from os.add_dll_directory
    """
    Wrapper aligned with the C wrapper’s flow:
      SiteInit(Y,X,Z) -> fill yy (no dd) -> CheckYY -> Init -> UpdateAfterImport -> (loop) Growth
    """
    def __init__(self, lib_path: str | Path, data_dir: Optional[str | Path] = None):
        self.data_dir = Path(data_dir) if data_dir else None
        lib_path = Path(lib_path).resolve()
        key = str(lib_path).lower()

        # Reuse a single FFI/dlopen per DLL path
        cached = Motti4DLL._LIB_CACHE.get(key)
        if cached:
            self.ffi, self.lib = cached
            return

        ffi = FFI()
        ffi.cdef(self._cdef_source())
        # Add DLL search dirs once; keep handles alive
        try:
            if hasattr(os, "add_dll_directory"):
                for p in (lib_path.parent, self.data_dir):
                    if p:
                        ps = str(Path(p).resolve())
                        if ps not in Motti4DLL._DLL_DIR_HANDLES:
                            Motti4DLL._DLL_DIR_HANDLES[ps] = os.add_dll_directory(ps)
        except AttributeError:
            pass

        lib: Any = ffi.dlopen(str(lib_path))
        Motti4DLL._LIB_CACHE[key] = (ffi, lib)
        self.ffi, self.lib = ffi, lib

    # ---------- helpers ----------

    @classmethod
    def auto_euref_km(cls, y: float, x: float) -> tuple[float, float]:
        """Public wrapper for coordinate normalization."""
        return cls._auto_euref_km(y, x)

    @classmethod
    def set_lib_cache(cls, key: str, value: tuple[object, object]) -> None:
        """Expose safe setter for LIB_CACHE (for tests)."""
        cls._LIB_CACHE[key] = value

    @classmethod
    def get_lib_cache(cls, key: str) -> tuple[object, object] | None:
        """Expose safe getter for LIB_CACHE (for tests)."""
        return cls._LIB_CACHE.get(key)

    @staticmethod
    def maybe_chdir(tmp_dir: Path | None = None):
        """Public wrapper around internal contextmanager _maybe_chdir."""
        return _maybe_chdir(tmp_dir)


    @property
    def param_290(self) -> float:
        # expose a public name
        return getattr(self, "_290", 0.0)
    
    @param_290.setter
    def param_290(self, value: float) -> None:
        self._290 = value

    def _has(self, name: str) -> bool:
        try:
            getattr(self.lib, name)
            return True
        except AttributeError:
            return False

    def convert_species_code(self, spe: int | float) -> int:
        # Prefer DLL helper; otherwise match the C wrapper policy (7->8, 8->9)
        if self._has("Convert_Tree_Spec"):
            try:
                return int(round(float(self.lib.Convert_Tree_Spec(float(spe)))))
            except AttributeError:
                pass
        s = int(spe)
        if s == 7:  # other conifers
            return 8
        if s == 8:  # other deciduous
            return 9
        return s

    def convert_site_index(self, mty: int | float) -> int:
        # Prefer DLL helper; otherwise cap <= 6 (matches their Convert_Site policy)
        if self._has("Convert_Site"):
            try:
                return int(round(float(self.lib.Convert_Site(int(mty)))))
            except AttributeError:
                pass
        return min(int(mty), 6)

    def _apply_overrides(self, yy, overrides: Optional[dict] = None):
        if not overrides:
            return
        # Allow explicit assignment of known scalar fields
        scalar_ok = {
            "mal", "mty", "verl", "verlt", "alr", "year", "step",
            "spedom", "spedom2", "nstorey", "gstorey",
            "lake", "sea"
        }
        for k, v in overrides.items():
            if k in scalar_ok and hasattr(yy, k):
                try:
                    setattr(yy, k, float(v))
                except AttributeError:
                    pass

    # ---------- FFI ----------

    def _cdef_source(self) -> str:
        return r"""
        typedef struct { float ma, ku, ra, hi, ha, hl, tl, mh, ml; } Motti4Spev9;
        typedef struct { float total, ma, ku, ra, hi, ha, hl, tl, mh, ml; } Motti4Spev10;
        typedef struct { float trunk, waste, branch_live, branch_dead, leaf, base, root_dense, root_thin; } Motti4Biomass;

        typedef struct {
            float id; float f; float spe; float age; float age13; float d13; float h; float cr; float snt;
            Motti4Spev10 ccftop; Motti4Spev10 bal;
            float vol; float vol_t; float vol_s; float vol_f; float waste; float destr; float crfix; float keh;
            float storie; float latraj; float crerror; float h0; float cr0; float crt; float d13_0; float sid;
            float fdead; float xd; float xg; float xh; float xvol; float xvol_dead; float ba; float _53; float thin1; float thin2;
            float _56[25]; Motti4Biomass bm; float _89[2];
        } Motti4Tree;
        typedef Motti4Tree Motti4Trees[1000];

        typedef struct { float spe, age, ba, f, h, hw, d, dg, storey, st, sid; } Motti4Stratum;
        typedef Motti4Stratum Motti4Strata[10];

        typedef struct {
            float year, age, hdom;
            float f_kkp, f_klv, f_vlj;
            float crfix_kkp, crfix_klv, crfix_vlj;
            float N_kkp, N_klv, N_vlj;
            float h_kkp, h_klv, h_vlj;
            float d_kkp, d_klv, d_vlj;
            float osid_kkp, osid_klv, osid_vlj;
            float age_kkp, age_klv, age_vlj;
            float age13_kkp, age13_klv, age13_vlj;
            float g_kkp, g_klv, g_vlj;
            float v_kkp, v_klv, v_vlj;
            float hg_kkp, hg_klv, hg_vlj;
            float dg_kkp, dg_klv, dg_vlj;
            float _40;
        } Motti4SaplingStratum;
        typedef struct { 
            Motti4SaplingStratum ma, ku, ra, hi, ha, hl, tl, mh, ml, _10; 
        } Motti4SaplingsSpev;
        typedef Motti4SaplingsSpev Motti4Saplings[10];

        typedef struct { float year, V0, N0, alr, _5, type, amount, p, phos, _10; } Motti4Fertilization;
        typedef float Motti4VcrArray[270];
        typedef float Motti4KorArray[2160];
        typedef Motti4Fertilization Motti4FerArray[10];

        typedef struct { int death_forest, death_tree, _3, _4, _5, _6, _7, _8, calibrate, _10; } Motti4Ctrl;

        typedef struct { float age100, h100, g, f, dg, spe; } Motti4StoreyInfo;

        typedef struct {
            float Y, X, Z, lake, sea, dd;
            float _7, _8, _9, _10;
            float rgn_nat_spe, rgn_seedratio, rgn_vlj_spe, rgn_f, rgn_surv, _16;
            float xt_regen, xt_muok, xt_raiv, xt_fert_prev;
            float mal, mty, verl, verlt, alr, pd, _27, muok, _29, _30;
            Motti4Spev9 si;
            float tkg;
            Motti4Spev9 hd50;
            float year, step, sid, _53, xt_perk, prt, fthin, xt_thin, xt_fert, fert_peat;
            float xt_thoit, drain, xt_ndrain, xt_rdrain, _64, _65, _66, _67, _68;
            float xt_kar, xt_fthin, agedom, agedom13, ndom, spedom, spedom2, dcond, kehl, nstorey, gstorey;
            Motti4StoreyInfo st1, st2, st3, st4, st12;
            Motti4Spev10 hdom100, hdom_j, hg, hf, ddom100, ddom_latv, dg, df;
            float h100_perk, crdom, crerror, rimp, vg, v1, v2, v3, v4, v12;
            Motti4Spev10 f, f13, G, ccf;
            float _240[10];
            Motti4Spev10 ccfi, V;
            float f_dead, ba_dead, v_dead, _273, _274, _275, _276, _277, jh, jd;
            Motti4Spev10 xhdom;
            float _290, ddomg0, dgdom0, ba0, h100_0, cr100_0, v0, dg0, _298, dgM, _300;
            float _yy2[301];
        } Motti4Site;

        void Motti4SiteInit(Motti4Site *yy, float *Y, float *X, float *Z, int *rv);
        void Motti4CheckYY(Motti4Site *yy, int *nerr, int *err);

        void Motti4Init(Motti4Strata *yo, Motti4Site *yy, Motti4Saplings *ut, Motti4KorArray *kor,
                        Motti4VcrArray *vcr, Motti4KorArray *apv, Motti4Trees *yp, Motti4Ctrl *o,
                        int *numtrees, int *err, int *rv);

        void Motti4UpdateAfterImport(Motti4Site *yy, Motti4Trees *yp, Motti4Saplings *ut,
                                     Motti4KorArray *kor, Motti4VcrArray *vcr, Motti4KorArray *apv,
                                     int *numtrees, int *rv);

        void Motti4Growth(Motti4Site *yy, Motti4Trees *yp, Motti4Saplings *ut, Motti4KorArray *kor,
                          Motti4VcrArray *vcr, Motti4KorArray *apv, int *numtrees, Motti4FerArray *fer,
                          int *numfer, Motti4Ctrl *o, int *step, int *rv);

        /* Optional helpers (best-effort) */
        double Convert_Tree_Spec(double Mela_tree_spec_in);
        float  Convert_Site(int Mela_site);
        void   Pack_Tree_Matrix(void);
        """

    # ---------- site + trees ----------

    @staticmethod
    def _auto_euref_km(y1: float, x1: float) -> Tuple[float, float]:
        # Helper if you accidentally pass meters or lat/long.
        abs_y, abs_x = abs(y1), abs(x1)
        if abs_y <= 90.0 and abs_x <= 180.0:
            raise ValueError(
                f"Coordinates look like lat/long (Y={y1}, X={x1}). "
                "Motti expects EUREF-FIN/TM35 in kilometers (e.g., Y~6900, X~3400)."
            )
        if abs_y > 10000.0 or abs_x > 10000.0:
            return y1 / 1000.0, x1 / 1000.0
        return y1, x1

    def new_site(
        self,
        *,
        Y: float, X: float, Z: float = -1.0,
        lake: float = 0.0, sea: float = 0.0,
        mal: int = 1, mty: int = 3, verl: int = 2, verlt: int = 0, alr: int = 1,
        year: Optional[float] = 2010.0,   # safe default if caller does not provide
        step: float = 5.0,
        convert_coords: bool = False,
        convert_mela_site: bool = True,
        overrides: Optional[dict] = None,
    ):
        """
        IMPORTANT: Matches C flow -> SiteInit first, then fill fields (no dd), then CheckYY.
        If Z is unknown, pass Z=-1.0 to let the DLL infer it.
        """
        ffi, lib = self.ffi, self.lib
        yy = cast(Any, ffi.new("Motti4Site *"))

        # 1) SiteInit with only Y,X,Z
        try:
            y_km, x_km = (self._auto_euref_km(Y, X) if convert_coords else (Y, X))
        except ValueError as e:
            raise RuntimeError(str(e)) from e

        rv = ffi.new("int *")
        with _maybe_chdir(self.data_dir):
            lib.Motti4SiteInit(yy,
                               ffi.new("float *", float(y_km)),
                               ffi.new("float *", float(x_km)),
                               ffi.new("float *", float(Z)),
                               rv)
        if rv[0] != 0:
            raise RuntimeError(f"Motti4SiteInit failed (rv={rv[0]})")

        # 2) Fill the rest (do NOT set yy.dd ourselves)
        yy.Y = float(y_km)
        yy.X = float(x_km)
        yy.Z = float(Z)
        yy.lake = float(lake)
        yy.sea = float(sea)
        yy.mal = float(mal)
        yy.mty = float(self.convert_site_index(mty) if convert_mela_site else mty)
        yy.verl = float(verl)
        yy.verlt = float(verlt)
        yy.alr = float(alr)
        if year is not None:
            yy.year = float(year)
        yy.step = float(step)
        # sensible defaults seen in the C wrapper
        yy.nstorey = 1.0
        yy.gstorey = 1.0

        # allow caller to override specific scalars (including spedom/spedom2)
        self._apply_overrides(yy, overrides)

        # 3) Validate
        nerr = ffi.new("int *")
        err = ffi.new("int *")
        with _maybe_chdir(self.data_dir):
            lib.Motti4CheckYY(yy, nerr, err)
        if nerr[0] != 0:
            raise RuntimeError(f"Motti4CheckYY signaled problem (nerr={nerr[0]}, err={err[0]})")

        return yy

    def new_trees(self, trees_py: Iterable[dict]) -> Tuple[object, int]:
        """
            fields used: id, f, d13, h, spe, age, age13, cr, snt
        """
        ffi = self.ffi
        yp = ffi.new("Motti4Trees *")
        numtrees = 0
        for i, t in enumerate(trees_py):
            yp[0][i].id = int(t.get("id", i + 1))
            yp[0][i].f = float(t.get("f", 0.0))
            yp[0][i].d13 = float(t.get("d13", 0.0))
            yp[0][i].h = float(t.get("h", 0.0))
            yp[0][i].spe = float(t.get("spe", 1))
            yp[0][i].age = float(t.get("age", 0.0))
            yp[0][i].age13 = float(t.get("age13", 0.0))
            yp[0][i].cr = float(t.get("cr", 0.0))
            yp[0][i].snt = float(t.get("snt", 1))
            yp[0][i].crerror = 0.0  # clear before growth
            numtrees += 1
        return yp, numtrees

    # ---------- full grow (Init -> UpdateAfterImport -> loop Growth) ----------

    def grow(
            self, yy, yp, numtrees: int, step: int = 5,
            ctrl: Optional[dict] = None, skip_init: bool = True
        ) -> GrowthDeltas:
        ffi, lib = self.ffi, self.lib
        strata = ffi.new("Motti4Strata *")
        saplings = ffi.new("Motti4Saplings *")
        kor_state = ffi.new("Motti4KorArray *")
        vcr_state = ffi.new("Motti4VcrArray *")
        apv_state = ffi.new("Motti4KorArray *")
        fert_array = ffi.new("Motti4FerArray *")
        mottiCtrl = cast(Any, ffi.new("Motti4Ctrl *"))
        # defaults like the C wrapper
        mottiCtrl.death_tree = 1
        if ctrl:
            if "death_tree" in ctrl:
                mottiCtrl.death_tree = int(bool(ctrl["death_tree"]))
            if "death_forest" in ctrl:
                mottiCtrl.death_forest = int(bool(ctrl["death_forest"]))
            if "calibrate" in ctrl:
                mottiCtrl.calibrate = int(bool(ctrl["calibrate"]))

        ntrees_p = ffi.new("int *", numtrees)
        err = ffi.new("int *")
        rv = ffi.new("int *")
        numfer = ffi.new("int *", 0)

        # Init (only when building trees inside DLL). With host trees, SKIP like the C wrapper.
        if not skip_init:
            with _maybe_chdir(self.data_dir):
                lib.Motti4Init(strata, yy, saplings, kor_state, vcr_state, apv_state, yp, mottiCtrl, ntrees_p, err, rv)
            if rv[0] != 0 or err[0] != 0:
                raise RuntimeError(f"Motti4Init failed (rv={rv[0]}, err={err[0]})")

        # UpdateAfterImport
        with _maybe_chdir(self.data_dir):
            lib.Motti4UpdateAfterImport(yy, yp, saplings, kor_state, vcr_state, apv_state, ntrees_p, rv)
        if rv[0] != 0:
            raise RuntimeError(f"Motti4UpdateAfterImport failed (rv={rv[0]})")

        # Accumulators keyed by tree id (order can change between sub-steps)
        acc_id: Dict[int, float] = {}
        acc_ih: Dict[int, float] = {}
        acc_if: Dict[int, float] = {}
        prev_f: Dict[int, float] = {int(yp[0][i].id): float(yp[0][i].f) for i in range(ntrees_p[0])}

        remaining = int(step)
        while remaining > 0:
            # reset like C wrapper
            try:
                yy.param_290 = 0.0
            except AttributeError:
                pass
            for i in range(ntrees_p[0]):
                yp[0][i].crerror = 0.0

            step_p = ffi.new("int *", remaining)
            rv[0] = 0
            with _maybe_chdir(self.data_dir):
                lib.Motti4Growth(yy, yp, saplings, kor_state, vcr_state, apv_state, ntrees_p, fert_array, numfer, mottiCtrl, step_p, rv)
            if rv[0] != 0:
                raise RuntimeError(f"Motti4Growth failed (rv={rv[0]})")

            for i in range(ntrees_p[0]):
                tid = int(yp[0][i].id)
                acc_id[tid] = acc_id.get(tid, 0.0) + float(yp[0][i].xd)
                acc_ih[tid] = acc_ih.get(tid, 0.0) + float(yp[0][i].xh)
                nf = float(yp[0][i].f)
                pf = prev_f.get(tid, nf)  # if first time we see tid, Δf=0
                acc_if[tid] = acc_if.get(tid, 0.0) + (nf - pf)
                prev_f[tid] = nf

            done = int(step_p[0])
            if done <= 0:
                break
            remaining -= done

        ids_now = [int(yp[0][i].id) for i in range(ntrees_p[0])]
        out_id = [acc_id.get(tid, 0.0) for tid in ids_now]
        out_ih = [acc_ih.get(tid, 0.0) for tid in ids_now]
        out_if = [acc_if.get(tid, 0.0) for tid in ids_now]

        return GrowthDeltas(tree_ids=ids_now, trees_id=out_id, trees_ih=out_ih, trees_if=out_if)
