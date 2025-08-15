
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple, Optional
import os
from contextlib import contextmanager

from cffi import FFI


@dataclass
class GrowthDeltas:
    trees_id: List[float]
    trees_ih: List[float]
    trees_if: List[float]


@contextmanager
def _maybe_chdir(tmp_dir: Optional[Path] = None):
    """Temporarily chdir into tmp_dir if provided (for DLLs that open relative .dat files)."""
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
    def __init__(self, lib_path: str | Path, data_dir: Optional[str | Path] = None):
        self.ffi = FFI()
        self.ffi.cdef(self._cdef_source())
        self.data_dir = Path(data_dir) if data_dir else None
        lib_path = Path(lib_path)
        try:
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(str(lib_path.parent))
                if self.data_dir:
                    os.add_dll_directory(str(self.data_dir))
        except Exception:
            pass
        self.lib = self.ffi.dlopen(str(lib_path))

    def _apply_overrides(self, yy, overrides: Optional[dict] = None):
        if not overrides:
            return

        # ---- map well-known yy2 fields to the raw array indices ----
        # In motti4.h, yy2 starts with index 1. So index = field_number - 1.
        # skip_gstorey is yy2 field #55  -> index 54 (0-based)
        YY2_MAP = {
            "skip_gstorey": 55,
            # add more if needed:
            # "itpl": 7, "yev": 8, "plerc": 9, "phak": 50, "xt_phak": 51, ...
        }

        for k, v in overrides.items():
            # first try regular attributes on yy
            try:
                setattr(yy, k, v)
                continue
            except AttributeError:
                pass

            # then try mapped yy2 fields
            fld = YY2_MAP.get(k)
            if fld is not None:
                try:
                    yy._yy2[fld - 1] = float(v)
                    continue
                except Exception:
                    pass





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

        typedef struct { float f, fdel, d13, h, _5[5]; } Motti4EarlyCareInfo;
        typedef struct { float meth, elop, spe, f, mm, raiv, spe_seed; } Motti4RegenParm;

        void Motti4SiteInit(Motti4Site *yy, float *Y, float *X, float *Z, int *rv);
        void Motti4Init(Motti4Strata *yo, Motti4Site *yy, Motti4Saplings *ut, Motti4KorArray *kor,
                        Motti4VcrArray *vcr, Motti4KorArray *apv, Motti4Trees *yp, Motti4Ctrl *o,
                        int *numtrees, int *err, int *rv);
        void Motti4UpdateAfterImport(Motti4Site *yy, Motti4Trees *yp, Motti4Saplings *ut,
                                     Motti4KorArray *kor, Motti4VcrArray *vcr, Motti4KorArray *apv,
                                     int *numtrees, int *rv);
        void Motti4Growth(Motti4Site *yy, Motti4Trees *yp, Motti4Saplings *ut, Motti4KorArray *kor,
                          Motti4VcrArray *vcr, Motti4KorArray *apv, int *numtrees, Motti4FerArray *fer,
                          int *numfer, Motti4Ctrl *o, int *step, int *rv);

        void Motti4CheckYY(Motti4Site *yy, int *nerr, int *err);
        """

    @staticmethod
    def _auto_euref_km(Y: float, X: float) -> Tuple[float, float]:
        absY, absX = abs(Y), abs(X)
        if absY <= 90.0 and absX <= 180.0:
            raise ValueError(
                f"Geo coordinates look like lat/long (Y={Y}, X={X}). "
                "Motti expects EUREF-FIN/TM35 in kilometers (e.g., Y~6900, X~3400)."
            )
        if absY > 10000.0 or absX > 10000.0:
            return Y / 1000.0, X / 1000.0
        return Y, X



    def new_site(
        self,
        *,
        Y: float, X: float, Z: float,
        dd: float,
        lake: float = 0.0, sea: float = 0.0,
        mal: int = 1, mty: int = 3, verl: int = 2, verlt: int = 0, alr: int = 1,
        year: float = 2025.0,
        step: float = 5.0,
        convert_coords: bool = True,
        overrides: Optional[dict] = None
    ):
        ffi = self.ffi
        yy = ffi.new("Motti4Site *")
        try:
            Y_km, X_km = (self._auto_euref_km(Y, X) if convert_coords else (Y, X))
        except ValueError as e:
            raise RuntimeError(str(e))

        yy.Y = Y_km; yy.X = X_km; yy.Z = Z
        yy.lake = lake; yy.sea = sea; yy.dd = dd
        yy.mal = float(mal); yy.mty = float(mty); yy.verl = float(verl); yy.verlt = float(verlt); yy.alr = float(alr)
        yy.year = float(year); yy.step = float(step)

        rv = ffi.new("int *")
        with _maybe_chdir(self.data_dir):
            self._apply_overrides(yy, overrides)
            self.lib.Motti4SiteInit(yy, ffi.new("float *", Y_km), ffi.new("float *", X_km), ffi.new("float *", Z), rv)

        if rv[0] != 0:
            nerr = ffi.new("int *"); err = ffi.new("int *")
            try:
                self._apply_overrides(yy, overrides)
                self.lib.Motti4CheckYY(yy, nerr, err)
            except Exception:
                pass
            hint = []
            if rv[0] == 1:
                hint.append("Generic failure.")
            elif rv[0] == 2:
                hint.append("Likely coordinate or data file issue (out-of-bounds EUREF-FIN km, or missing *.dat files).")
            elif rv[0] == 3:
                hint.append("Parameter domain error (site attributes).")
            if self.data_dir and not os.path.isdir(self.data_dir):
                hint.append(f"data_dir does not exist: {self.data_dir}")
            raise RuntimeError(
                f"Motti4SiteInit failed (rv={rv[0]}, nerr={nerr[0] if nerr else 'NA'}, err={err[0] if err else 'NA'}). "
                + (" ".join(hint) if hint else "")
            )
        return yy

    def check_site(
        self,
        *,
        Y: float, X: float, Z: float, dd: float,
        lake: float = 0.0, sea: float = 0.0,
        mal: int = 1, mty: int = 3, verl: int = 2, verlt: int = 0, alr: int = 1,
        year: float = 2025.0, step: float = 5.0,
        convert_coords: bool = True,
        overrides: Optional[dict] = None
    ):
        ffi, lib = self.ffi, self.lib
        yy = ffi.new("Motti4Site *")
        try:
            Y_km, X_km = (self._auto_euref_km(Y, X) if convert_coords else (Y, X))
        except ValueError as e:
            return {"error": str(e)}
        yy.Y = Y_km; yy.X = X_km; yy.Z = Z
        yy.lake = lake; yy.sea = sea; yy.dd = dd
        yy.mal = float(mal); yy.mty = float(mty); yy.verl = float(verl); yy.verlt = float(verlt); yy.alr = float(alr)
        yy.year = float(year); yy.step = float(step)
        self._apply_overrides(yy, overrides)
        nerr = ffi.new("int *"); err = ffi.new("int *")
        try:
            lib.Motti4CheckYY(yy, nerr, err)
            return {
                "nerr": int(nerr[0]), "err": int(err[0]),
                "Y": Y_km, "X": X_km, "Z": Z, "dd": dd, "lake": lake, "sea": sea,
                "mal": mal, "mty": mty, "verl": verl, "verlt": verlt, "alr": alr, "year": year, "step": step
            }
        except Exception as ex:
            return {"error": f"CheckYY call failed: {ex}"}

    def new_trees(self, trees_py: Iterable[dict]) -> Tuple[object, int]:
        ffi = self.ffi
        yp = ffi.new("Motti4Trees *")
        numtrees = 0
        for i, t in enumerate(trees_py):
            yp[0][i].id = float(i+1)
            yp[0][i].f = float(t.get("f", 0.0))
            yp[0][i].d13 = float(t.get("d13", 0.0))
            yp[0][i].h = float(t.get("h", 0.0))
            yp[0][i].spe = float(t.get("spe", 1))
            yp[0][i].age = float(t.get("age", 0.0))
            yp[0][i].age13 = float(t.get("age13", 0.0))
            yp[0][i].cr = float(t.get("cr", 0.4))
            yp[0][i].snt = float(t.get("snt", 1))
            numtrees += 1
        return yp, numtrees

    def grow(self, yy, yp, numtrees: int, step: int = 5) -> GrowthDeltas:
        ffi, lib = self.ffi, self.lib
        yo = ffi.new("Motti4Strata *")
        ut = ffi.new("Motti4Saplings *")
        kor = ffi.new("Motti4KorArray *")
        vcr = ffi.new("Motti4VcrArray *")
        apv = ffi.new("Motti4KorArray *")
        fer = ffi.new("Motti4FerArray *")
        o = ffi.new("Motti4Ctrl *")
        ntrees_p = ffi.new("int *", numtrees)
        err = ffi.new("int *")
        rv = ffi.new("int *")
        numfer = ffi.new("int *", 0)
        step_p = ffi.new("int *", step)

        lib.Motti4Init(yo, yy, ut, kor, vcr, apv, yp, o, ntrees_p, err, rv)
        if rv[0] != 0 or err[0] != 0:
            raise RuntimeError(f"Motti4Init failed (rv={rv[0]}, err={err[0]})")

        lib.Motti4Growth(yy, yp, ut, kor, vcr, apv, ntrees_p, fer, numfer, o, step_p, rv)
        if rv[0] != 0:
            raise RuntimeError(f"Motti4Growth failed (rv={rv[0]})")

        trees_id, trees_ih, trees_if = [], [], []
        for i in range(ntrees_p[0]):
            trees_id.append(float(yp[0][i].xd))
            trees_ih.append(float(yp[0][i].xh))
            trees_if.append(0.0)
        return GrowthDeltas(trees_id=trees_id, trees_ih=trees_ih, trees_if=trees_if)