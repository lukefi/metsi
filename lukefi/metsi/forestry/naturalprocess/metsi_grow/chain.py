import dataclasses
from functools import cached_property
from itertools import compress
from typing import Any, Callable, Container, Dict, List, Mapping, Optional, Sequence, TypeVar
import numpy as np
import numpy.typing as npt
from .aggr import ba_seed, ba_spe, baL_spe, ccfL_spe, ddom100_spe, dg, dgdom, dot, hdom100_spe, prefixsum_level, spedom_d, spedom_f, spedom_g, xdom100_storie, xdomj, xg_subseq
from .ccf import ccf, ccfi
from .coding import AddedPhosphorus, DitchCondition, DitchStatus, FertilizerType, LandUseCategoryVMI, Origin, PeatTypeSINKA, SaplingType, SiteTypeVMI, SoilCategoryVMI, SoilPrep, Species, Storie, TaxClass, TaxClassReduction, TkgTypeVasanderLaine
from .coord import etrs_tm35_to_ykj
from .cr import cr
from .crk import crkv0, hkan, ucrkdbh
from .death import bmodel3_suo_koivu, famort, jsdeath_interp, jsdeath_kuusi, pmodel3a_suo_manty
from .distrib import rakenne
from .f import frel_perk, ikaero_comp
from .fert import fert_a, fert_b, ih_hpros, iv_fert, iv_rf_mot
from .hd50 import hd50, hind
from .id import id5_suo_koivu, id5_suo_kuusi, id5_suo_manty, id_init
from .ig import ig5_figu
from .ih import hincu, ih5_fihu, ih5_suo_koivu, ih5_suo_kuusi, ih5_suo_manty, ih5adj
from .kanto import dk, dkjs_small
from .kor import xkor
from .lasum import ilmanor
from .pt import Pt, PtOpt, ptalku, ptsurvjs
from .regen import Tapula, agekri_empty, synt, tapula_luont, tapula_vilj
from .rules import growing_storie, muok_default, ndistrib, promote_lower_storie
from .strata import group_strata
from .thin import self_thin_mineral_12, self_thin_mineral_34, self_thin_peat_12, self_thin_peat_34
from .tkg import turvekangas
from .trans import ba2d, d2ba
from .typing import Ints, Reals, update_wrapper_generic
from .vol import vol

__all__ = [
    "Predict",
    "predict"
]

_sentinel = object()

class CachedSequence(list):
    def __init__(self, f, num=None):
        self.f = f
        if num:
            self.extend(_sentinel for _ in range(num))
    def __getitem__(self, i):
        if i >= len(self):
            self.extend(_sentinel for _ in range(i-len(self)+1))
        x = super().__getitem__(i)
        if x is _sentinel:
            x = self.f(i)
            self[i] = x
        return x
    def __iter__(self):
        yield from (self[i] for i in range(len(self)))

class CachedMapping(dict):
    def __init__(self, f):
        self.f = f
    def __getitem__(self, k):
        try:
            return super().__getitem__(k)
        except KeyError:
            self[k] = self.f(k)
            return self[k]

T, U = TypeVar("T"), TypeVar("U")
def cached_sequence(
    *,
    num: Optional[Callable[[U], int]]
) -> Callable[[Callable[[U, int], T]], cached_property[List[T]]]:
    def w(f: Callable[[U, int], T]) -> cached_property[List[T]]:
        return cached_property(update_wrapper_generic(
            lambda self: CachedSequence(lambda i: f(self, i), num and num(self)),
            f,
            generic = CachedSequence
        ))
    return w

K = TypeVar("K")
def cached_mapping(f: Callable[[Any, K], T]) -> cached_property[Dict[K, T]]:
    return cached_property(update_wrapper_generic(
        lambda self: CachedMapping(lambda k: f(self, k)),
        f,
        generic = CachedMapping
    ))

# the following return types are Any because cached properties confuse pyright

def root(name) -> Any:
    def _raise(self):
        raise KeyError(f"missing root: {name}")
    return cached_property(_raise)

class _ResultProperty:
    def __init__(self, f):
        self.f = f
    def __set_name__(self, _owner, name):
        self.attr = name
    def __get__(self, obj, _owner=None):
        self.f(obj)
        return obj.__dict__[self.attr]

def result_property(f: Callable[[Any], None]) -> Any:
    return _ResultProperty(f)

class _InitMixin:
    def __init__(self, **kw):
        for k,v in kw.items():
            setattr(self, k, v)

#---- site variables prediction ----------------------------------------

class CachedStorie(_InitMixin):
    predict: "Predict" = root("predict")
    which: Storie = root("which")

    def _x100(self, xs: Reals) -> float:
        flt = (s == self.which for s in self.predict.trees_storie)
        if self.which == self.predict.growing_storie:
            flt = (f and s == self.predict.spedom for f,s in zip(flt, self.predict.trees_spe))
        return xdom100_storie(
            xs = xs,
            d = self.predict.trees_dnz,
            f = self.predict.trees_f,
            snt = self.predict.trees_snt,
            flt = flt,
            prt = self.predict.prt
        )

    @cached_property
    def age100(self) -> float:
        """Mean age of 100 largest trees (``year``) by diameter."""
        return self._x100(self.predict.trees_age)

    @cached_property
    def h100(self) -> float:
        """Mean height of 100 largest trees (``m``) by diameter."""
        return self._x100(self.predict.trees_h)

    @cached_property
    def g(self) -> float:
        """Total basal area (``m^2/ha``)."""
        return sum(f*g for f,g,s
                   in zip(self.predict.trees_f, self.predict.trees_ba, self.predict.trees_storie)
                   if s == self.which)

    @cached_property
    def f(self) -> float:
        """Total stem count (``1/ha``)."""
        return sum(f for f,s
                   in zip(self.predict.trees_f, self.predict.trees_storie)
                   if s == self.which)

    @cached_property
    def dg(self) -> float:
        """Basal-area weighted mean diameter (``cm``)."""
        if self.which == Storie.RETENTION:
            return 0
        flt = (s == self.which for s in self.predict.trees_storie)
        if self.which == self.predict.growing_storie:
            flt = (f and s == self.predict.spedom for f,s in zip(flt, self.predict.trees_spe))
        s3, s2 = 0, 0
        for f,d in compress(zip(self.predict.trees_f, self.predict.trees_dnz), flt):
            s2 += f*d**2
            s3 += f*d**3
        return s3/s2 if s2 > 0 else 0

    @cached_property
    def spe(self) -> Species:
        """Main species."""
        if self.which == self.predict.growing_storie:
            return self.predict.spedom
        if self.h100 < 3:
            return spedom_f(
                (sp,f) for sp,f,s
                in zip(self.predict.trees_spe, self.predict.trees_f, self.predict.trees_storie)
                if s == self.which
            )
        sfd = (
            (sp,f,d) for sp,f,d,s
            in zip(self.predict.trees_spe, self.predict.trees_f, self.predict.trees_dnz,
                   self.predict.trees_storie)
            if s == self.which
        )
        return spedom_d(sfd) if self.h100 < 5 else spedom_g(sfd)

class Predict(_InitMixin):

    #-- site --------------------

    year: float = root("year")
    """Current simulation year."""

    mal: LandUseCategoryVMI = root("mal")
    """Land use category."""

    mty: SiteTypeVMI = root("mty")
    """Site type."""

    alr: SoilCategoryVMI = root("alr")
    """Soil category."""

    verl: TaxClass = root("verl")
    """Tax class."""

    verlt: TaxClassReduction = TaxClassReduction.NONE
    """Tax class reduction."""

    oji: Optional[DitchStatus] = None
    """Ditching status."""

    ojik: Optional[DitchCondition] = None
    """Ditching condition. This has no effect on mineral soils."""

    #-- site / peat vars --------------------

    sty: Optional[PeatTypeSINKA] = None
    """Peat type. This has no effect on mineral soils."""

    rimp: bool = False
    """Rimpisyys."""

    pd: float = 0
    """Peat depth (``cm``). This has no effect on mineral soils."""

    #-- management --------------------

    spedom: Species = root("spedom")
    """Main species."""

    prt: Origin = root("prt")
    """Origin of trees (ie. method of last regeneration)."""

    h100_perk: Optional[float] = None
    """Dom100 height of the growing storie before previous tending of saplings (``m``)."""

    muok: Optional[SoilPrep] = None
    """Method of previous soil preparation."""

    t_muok: Optional[float] = None
    """Time of previous soil preparation (maanmuokkaus)."""

    t_thin: Optional[float] = None
    """Time of previous thinning (harvennus)."""

    t_regen: Optional[float] = None
    """Time of previous regeneration (uudistaminen)."""

    t_thoit: Optional[float] = None
    """Time of previous PCT (taimikonhoito)"""

    t_perk: Optional[float] = None
    """Time of previous tending of saplings (varhaisperkaus)."""

    t_fert: Optional[float] = None
    """Time of previous fertilization."""

    t_synt: Optional[float] = None
    """Time of previous natural birth of saplings."""

    t_ndrain: Optional[float] = None
    """Time of previous redraining (kunnostusojitus)."""

    t_rdrain: Optional[float] = None
    """Time of previous draining (uudisojitus)."""

    rt_synt: float = 0
    """Stem count of previous naturally regenerated saplings (``1/ha``)."""

    jh: float = 0
    """Extra height effect for cultivated seedlings."""

    jd: float = 0
    """Extra diameter effect for cultivated seedlings."""

    @cached_property
    def default_muok(self) -> Optional[SoilPrep]:
        if self.prt == Origin.NATURAL or self.muok is not None:
            return self.muok
        return muok_default(self.mty, self.alr)

    def _elapsed(self, since: Optional[float], step: float = 0) -> float:
        if since is None:
            return -1
        return self.year+step - since

    #-- trees --------------------

    trees_f: Reals = ()
    """Trees frequency (stem count) vector (``1/ha``)."""

    trees_d: Reals = ()
    """Trees raw (unclamped) diameter."""

    trees_h: Reals = ()
    """Trees height vector (``m``). """

    trees_ch_min: Optional[Reals] = None
    """Trees minimum crown height vector (``m``). """

    trees_spe: Sequence[Species] = ()
    """Trees species vector."""

    trees_t0: Reals = ()
    """Trees biological birth time vector (``year``)."""

    trees_t13: Reals = ()
    """Trees 1.3m height time vector (``year``)."""

    trees_storie: Sequence[Storie] = ()
    """storie vector."""

    trees_snt: Sequence[Origin] = ()
    """Trees origin vector."""

    @property
    def num_trees(self) -> int:
        """``numtrees``: Sample tree count."""
        return len(self.trees_f)

    @cached_sequence(num=num_trees.__get__)
    def trees_dnz(self, i) -> float:
        """Trees _nonzero_ diameter on mineral soil (at breast height, 1.3m) vector (``cm``)."""
        d = self.trees_d[i]
        if self.alr == SoilCategoryVMI.MINERAL and not d:
            return 0.01
        return d

    @cached_sequence(num=num_trees.__get__)
    def trees_ba(self, i) -> float:
        """Trees basal area vector (``m^2/ha``)."""
        return d2ba(self.trees_dnz[i])

    @cached_sequence(num=num_trees.__get__)
    def trees_age(self, i) -> float:
        """Trees biological age vector (``year``). """
        return self.year - self.trees_t0[i]

    @cached_sequence(num=num_trees.__get__)
    def trees_age13(self, i) -> float:
        """Trees breast height age vector (``year``)."""
        return self.year - self.trees_t13[i]

    @cached_sequence(num=num_trees.__get__)
    def trees_ccf(self, i) -> float:
        """Trees crown competition factor (minimum growing space) vector."""
        return _ccfD(self, i, self.trees_dnz[i])

    @cached_sequence(num=num_trees.__get__)
    def trees_ccfi(self, i) -> float:
        """Trees crown competition factor *independent of site variables*."""
        return ccfi(
            spe = self.trees_spe[i],
            f = self.trees_f[i],
            d = self.trees_dnz[i],
            h = self.trees_h[i]
        )

    @cached_sequence(num=num_trees.__get__)
    def trees_cr_raw(self, i) -> float:
        if self.trees_h[i] < 1.3:
            return 0.6
        else:
            return cr(
                spe = self.trees_spe[i],
                rdfl = self.trees_ccfL[Species][i],
                mty = self.mty,
                dd = self.dd,
                dg = self.dg,
                hg = self.hg[Species],
                rdf = self.rdf[Species]
            )

    @cached_sequence(num=num_trees.__get__)
    def trees_ch(self, i) -> float:
        """Trees crown height vector (``m``)."""
        chraw = (1 - self.trees_cr_raw[i]) * self.trees_h[i]
        if self.trees_ch_min is not None:
            return max(chraw, self.trees_ch_min[i])
        else:
            return chraw

    @cached_sequence(num=num_trees.__get__)
    def trees_cr(self, i) -> float:
        """Trees crown ratio vector."""
        return 1 - self.trees_ch[i]/self.trees_h[i]

    def _tree_vol(self, i):
        v = vol(
            spe = self.trees_spe[i],
            d = self.trees_dnz[i],
            h = self.trees_h[i]
        )
        self.trees_v_tot[i] = v.tot
        self.trees_v_saw[i] = v.saw
        self.trees_v_pulp[i] = v.pulp
        self.trees_v_waste[i] = v.waste

    @cached_sequence(num=num_trees.__get__)
    def trees_v_tot(self, i) -> float:
        """Trees total volume (``m^3``). Computed using a table model."""
        self._tree_vol(i)
        return self.trees_v_tot[i]

    @cached_sequence(num=num_trees.__get__)
    def trees_v_saw(self, i) -> float:
        self._tree_vol(i)
        return self.trees_v_saw[i]

    @cached_sequence(num=num_trees.__get__)
    def trees_v_pulp(self, i) -> float:
        self._tree_vol(i)
        return self.trees_v_pulp[i]

    @cached_sequence(num=num_trees.__get__)
    def trees_v_waste(self, i) -> float:
        self._tree_vol(i)
        return self.trees_v_waste[i]

    #-- tree aggregates --------------------

    @cached_mapping
    def trees_baL(self, spe: Container[Species]) -> List[float]:
        """Basal area sum of trees with larger diameter (``m^2/ha``)."""
        if self.num_trees == 1:
            return [0]
        baL, = baL_spe(ba=self.trees_ba, f=self.trees_f, spe=self.trees_spe, choose=(spe, ))
        return baL

    @cached_mapping
    def trees_ccfL(self, spe: Container[Species]) -> List[float]:
        """CCF sum of trees with larger diameter."""
        if self.num_trees == 1:
            return [0]
        ccfL, = ccfL_spe(prio=self.trees_dnz, ccf=self.trees_ccf, spe=self.trees_spe, choose=(spe, ))
        return ccfL

    #-- strata --------------------

    strata_t0: Reals = ()
    """Strata birth year vector. """

    strata_f: Reals = ()
    """Strata frequency (stem count) vector (``1/ha``). """

    strata_g: Optional[Reals] = None
    """Strata basal area vector (``m^2/ha``)."""

    strata_h: Reals = ()
    """Strata height vector (``m``). """

    strata_level: Ints = ()
    """Strata level vector."""

    strata_spe: Sequence[Species] = ()
    """Strata species vector."""

    strata_type: Sequence[SaplingType] = ()
    """Strata type vector."""

    strata_pvkor: Optional[npt.NDArray[np.float64]] = None
    """Old stratum matrix and adjustment matrix."""

    @property
    def num_strata(self) -> int:
        """Stratum vector length."""
        return len(self.strata_t0)

    @cached_sequence(num=num_strata.__get__)
    def strata_agex(self, i) -> float:
        if (
            self.strata_level[i] >= 3
            and self.t_perk is not None and
            self.strata_type[i] != SaplingType.CULTIVATED
        ):
            return self._elapsed(self.t_perk)
        else:
            return self.year - self.strata_t0[i]

    @cached_sequence(num=num_strata.__get__)
    def strata_snt(self, i) -> Origin:
        if self.strata_type[i] == SaplingType.CULTIVATED:
            return Origin.PLANTED if self.strata_level[i] >= 2 else self.prt
        else:
            return Origin.NATURAL

    @cached_property
    def strata_order(self) -> List[int]:
        return sorted(range(self.num_strata), key = lambda i: (
            self.strata_level[i],
            self.strata_spe[i],
            (self.strata_type[i]+1)%3  # TODO: just make the coding
        ))

    #-- strata aggregates --------------------

    @cached_property
    def f_small(self) -> float:
        return sum(f for f,h in zip(self.strata_f, self.strata_h) if h>0)

    #-- fertilizations --------------------

    fert_type: Sequence[FertilizerType] = ()
    """Fertilizer type vector."""

    fert_p: Sequence[AddedPhosphorus] = ()
    """Fertilizer phosphorus dummy vector. Only affects mineral soils."""

    fert_pkg: Reals = ()
    """Amount of phosphorus added (``kg``). Only affects peatlands."""

    fert_amt: Reals = ()
    """Fertilizer amount vector (``kg``). Only affects mineral soils."""

    fert_year: Reals = ()
    """Year vector of fertilizations."""

    fert_V0: Reals = ()
    """Stand volume at time of fertilization (``m^3/ha``). Only affets peatlands."""

    fert_N0: Reals = ()
    """Stand stem count at time of fertilization (``1/ha``). Only affects peatlands."""

    fert_level: float = 0.85
    """Fertilization effect coefficient."""

    @property
    def num_fert(self) -> int:
        """Number of fertilizations done."""
        return len(self.fert_year)

    #-- coordinates --------------------

    X: float = root("X")
    """ETRS-TM35FIN east coordinate (``km``). """

    Y: float = root("Y")
    """ETRS-TM35FIN north coordinate (``km``)."""

    def _ykj(self):
        Y_ykj, X_ykj = etrs_tm35_to_ykj(Y=self.Y, X=self.X)
        self.__dict__.update(Y_ykj=Y_ykj, X_ykj=X_ykj)

    X_ykj: float = result_property(_ykj)
    """YKJ east coordinate (``km``)."""

    Y_ykj: float = result_property(_ykj)
    """YKJ north coordinate (``km``)."""

    @cached_property
    def Z(self) -> float:
        """Height above sea level (``m``)."""
        return xkor(Y_ykj=self.Y_ykj, X_ykj=self.X_ykj)

    #-- weather parameters --------------------

    def _weather(self):
        weather = ilmanor(Y_ykj=self.Y_ykj, X_ykj=self.X_ykj, Z=self.Z)
        self.__dict__.update(
            dd = weather.dd,
            lake = weather.lake,
            sea = weather.sea
        )

    lake: float = result_property(_weather)
    """Lake index."""

    sea: float = result_property(_weather)
    """Sea index."""

    dd: float = result_property(_weather)
    """Average yearly temperature sum (``°C * day``)."""

    #-- tkg --------------------

    @cached_property
    def tkg(self) -> Optional[TkgTypeVasanderLaine]:
        """Turvekangas-type (XXX: english?)."""
        return turvekangas(
            mty = self.mty,
            alr = self.alr,
            spedom = self.spedom
        )

    #-- ditching --------------------

    @cached_property
    def pdr(self) -> bool:
        """*'Draining needed?'*-dummy."""
        if self.ojik == DitchCondition.GOOD:
            return False
        vlim = 125.0 if self.dd >= 1000.0 else 150.0
        return self.V < vlim

    #-- stone/peat --------------------

    @cached_property
    def ptkiv(self) -> float:
        """Stoniness factor."""
        if self.alr > SoilCategoryVMI.MINERAL and self.mal == LandUseCategoryVMI.FOREST:
            if self.oji in (DitchStatus.PEAT_UNDITCHED, DitchStatus.PEAT_UNAFFECTED):
                return 1
            if self.oji is None:
                return 0
        return float(self.verlt in (TaxClassReduction.STONY, TaxClassReduction.MOSS))

    @cached_property
    def ptsois(self) -> float:
        """Peat factor."""
        if self.alr > SoilCategoryVMI.MINERAL and self.mal == LandUseCategoryVMI.FOREST:
            if self.oji == DitchStatus.PEAT_UNDITCHED:
                return 1.5
            if self.oji in (DitchStatus.PEAT_UNAFFECTED, DitchStatus.PEAT_AFFECTED):
                return 1
            if self.oji is None:
                return 0
        return float(self.verlt == TaxClassReduction.WET)

    #-- stories --------------------

    @cached_mapping
    def storie(self, which: Storie) -> CachedStorie:
        """Storie information."""
        return CachedStorie(predict=self, which=which)

    @cached_property
    def growing_storie(self) -> Storie:
        """The current growing storie."""
        _, gs = growing_storie(
            storie = self.trees_storie,
            spe = self.trees_spe,
            spedom = self.spedom,
            small = self.num_strata > 0
        )
        return gs

    @cached_property
    def promote_lower_storie(self) -> bool:
        return promote_lower_storie(
            f_lower = (
                self.storie[Storie.LOWER].f
                + sum(f for f,l in zip(self.strata_f, self.strata_level) if l == 1)
            ),
            f_upper = self.storie[Storie.UPPER].f,
            h100_lower = self.storie[Storie.LOWER].h100,
            h100_upper = self.storie[Storie.UPPER].h100
        )

    @cached_property
    def st12_g_trees(self) -> float:
        return self.storie[Storie.LOWER].g + self.storie[Storie.UPPER].g

    @cached_property
    def st12_age100(self) -> float:
        h100 = self.storie[self.growing_storie].h100
        if self.st12_g_trees > 0 and h100 > 0:
            return self.storie[self.growing_storie].age100
        elif self.growing_stratum is not None:
            return self.strata_agex[self.growing_stratum]
        else:
            return 0

    @cached_property
    def st12_h100(self) -> float:
        h100 = self.storie[self.growing_storie].h100
        if self.st12_g_trees > 0 and h100 > 0:
            return h100
        elif self.growing_stratum is not None:
            return self.strata_attrs.h100[self.growing_stratum]
        else:
            return 0

    @cached_property
    def st12_g(self) -> float:
        """Growing storie basal area (``m^2/ha``)."""
        return self.st12_g_trees + sum(self.strata_attrs.g)

    @cached_property
    def st12_dg(self) -> float:
        """Growing storie basal area-weighted diameter (``cm``)."""
        if self.growing_stratum is not None:
            return self.strata_attrs.dgm[self.growing_stratum]
        else:
            return self.storie[self.growing_storie].dg

    @cached_property
    def st12_spe(self) -> Species:
        """Growing storie main species."""
        return self.spedom # varmaankin?

    #-- site-wide aggregates --------------------

    @cached_property
    def F(self) -> float:
        """Total stem count **including strata** (``1/ha``)."""
        return sum(self.trees_f) + sum(self.strata_f)

    @cached_mapping
    def G(self, spe: Container[Species]) -> float:
        """Total basal area of big trees (``m^2/ha``)."""
        return ba_spe(
            ba = [self.trees_ba[i] for i in range(self.num_trees)],
            f = self.trees_f,
            spe = self.trees_spe,
            choose = spe
        )

    @cached_property
    def V(self) -> float:
        """Total volume of big trees (``m^3/ha``)."""
        return dot(self.trees_f, self.trees_v_tot)

    @cached_property
    def G_seed(self) -> float:
        return ba_seed(self.trees_f, self.trees_dnz, self.trees_storie)

    @cached_property
    def Grel_lehti(self) -> float:
        if self.G[Species] > 0:
            return self.G[Species.DOWNY_BIRCH, Species.SILVER_BIRCH] / self.G[Species]
        else:
            return 0.2 if self.spedom in (Species.PINE, Species.SPRUCE) else 0.8

    @cached_property
    def Grel_manty(self) -> float:
        if self.G[Species] > 0:
            return self.G[Species.PINE, ] / self.G[Species]
        else:
            return 0.8 if self.spedom in (Species.PINE, Species.SPRUCE) else 0.2

    @cached_mapping
    def hdom100(self, spe: Container[Species]) -> float:
        """Average height of 100 largest trees (``m``) by diameter."""
        hdom100, = hdom100_spe(
            h = self.trees_h,
            f = self.trees_f,
            d = self.trees_dnz,
            storie = self.trees_storie,
            spe = self.trees_spe,
            choose = (spe, ),
            grow = self.growing_storie
        )
        return hdom100

    @cached_mapping
    def ddom100(self, spe: Container[Species]) -> float:
        """Average diameter of 100 largest trees (``cm``) by diameter."""
        ddom100, = ddom100_spe(
            f = self.trees_f,
            d = self.trees_dnz,
            storie = self.trees_storie,
            spe = self.trees_spe,
            choose = (spe, ),
            grow = self.growing_storie
        )
        return ddom100

    @cached_property
    def dgdom(self) -> float:
        return dgdom(
            d = self.trees_dnz,
            f = self.trees_f,
            spe = self.trees_spe,
            storie = self.trees_storie,
            spedom = self.spedom,
            grow = self.growing_storie
        )

    @cached_property
    def dg(self) -> float:
        """Big trees basal-area weighted mean diameter (``cm``)."""
        return dg(self.trees_dnz, self.trees_f)

    @cached_mapping
    def hg(self, spe: Container[Species]) -> float:
        """Big trees basal-area weighted mean height (``m``)."""
        return xg_subseq(
            x = self.trees_h,
            d = self.trees_dnz,
            f = self.trees_f,
            subseq = (sp in spe and st < Storie.OVER
                      for sp,st in zip(self.trees_spe, self.trees_storie))
        )

    @cached_mapping
    def rdf(self, spe: Container[Species]) -> float:
        """CCF (:attr:`trees_ccf`) sum over big trees."""
        return sum(ccf for ccf,s in zip(self.trees_ccf, self.trees_spe) if s in spe)

    @cached_property
    def rdfi(self) -> float:
        """CCFI (:attr:`trees_ccfi`) sum over big trees."""
        return sum(self.trees_ccfi)

    @cached_property
    def hdomj(self) -> float:
        """Arithmetic mean height of trees with diameter larger than :attr:`dg` (``m``)."""
        return xdomj(
            x = self.trees_h,
            f = self.trees_f,
            d = self.trees_dnz,
            dlim = self.dg
        )

    @cached_property
    def ddomj(self) -> float:
        """Arithmetic mean diameter of trees with diameter larger than :attr:`dg` (``cm``)."""
        return xdomj(
            x = self.trees_dnz,
            f = self.trees_f,
            d = self.trees_dnz,
            dlim = self.dg
        )

    #-- site index --------------------

    @cached_property
    def hd50(self) -> Mapping[Species, float]:
        """Predicted dominant height at age 50 (``m``) (pituusboniteetti)."""
        hfr = hd50(
            mty = self.mty,
            mal = self.mal,
            verl = self.verl,
            verlt = self.verlt,
            dd = self.dd,
            xj = self.lake,
            xm = self.sea,
            Z = self.Z,
            prt = self.prt,
            spedom = self.spedom,
            # XXX: motin bugi: EstimateHd50 kutsutaan ennen SetCCFFIOfTrees, joten se on kutsussa
            # aina 0. olisiko tässä tarkoitus olla `ccfi = self.rdfi`?
            ccfi = 0
        )
        return {sp:hfr[sp-1] for sp in Species}

    @cached_mapping
    def si(self, spe: Species) -> float:
        """Site index"""
        return hind(
            spe = spe,
            mty = self.mty,
            verlt = self.verlt,
            dd = self.dd,
            xj = self.sea,
            xm = self.lake,
            Z = self.Z
        )

    #-- strata ----------------------------------------

    @cached_property
    def strata_grouping(self) -> List[int]:
        return group_strata(self.strata_type, self.strata_level)

    @cached_property
    def level_rltot(self) -> List[float]:
        return prefixsum_level(self.strata_f, self.strata_grouping)

    @cached_property
    def strata_attrs(self) -> "StrataAttrs":
        return StrataAttrs(predict=self, step=0)

    @cached_property
    def growing_stratum(self) -> Optional[int]:
        return next(
            (i for i in range(self.num_strata)
             if (
                 self.strata_level[i] == 1
                 and self.strata_spe[i] == self.spedom
                 and self.strata_type[i] == SaplingType.CULTIVATED
             )), None)

    #-- natural processes ----------------------------------------

    def evolve(
        self,
        step: float = 5.0,
        tree_death: bool = True,
        self_thinning: bool = True
    ) -> "Evolve":
        """Creates an evolution model chain."""
        return Evolve(
            predict = self,
            step = step,
            tree_death = tree_death,
            self_thinning = self_thinning
        )

    def evolve_strata(
        self,
        step: float = 5.0,
        rdfl_skip: bool = False
    ) -> "StrataAttrs":
        """Creates a stratum attribute prediction chain."""
        return StrataAttrs(
            predict = self,
            step = step,
            rdfl_skip = rdfl_skip
        )

    #-- tree creation ----------------------------------------

    def create_trees(
        self,
        idx: Ints,
        step: float = 5.0,
        flim: float = 50.0
    ) -> "CreateTrees":
        """Creates a tree creation model chain."""
        return CreateTrees(
            predict = self,
            idx = idx,
            step = step,
            flim = flim
        )

    #-- regeneration ----------------------------------------

    def planting(
        self,
        spe: Species,
        f: float,
        snt: Origin,
        surv: float
    ) -> "Regenerate":
        """Creates a regeneration model chain for planting."""
        return Regenerate(
            predict = self,
            vspe = spe,
            vf = f,
            snt = snt,
            surv = surv,
            tapula = tapula_vilj(vpl=spe)
        )

    def natregen(
        self,
        spe: Optional[Species] = None
    ) -> "Regenerate":
        """Creates a regeneration model chain for natural regeneration."""
        tapula = tapula_luont(
            alr = self.alr,
            mty = self.mty,
            dd = self.dd,
            G_seed = self.G_seed,
            retaos = 0.5,
            kpl = spe or self.spedom,
            ypl = spe or self.spedom
        )
        return Regenerate(
            predict = self,
            tapula = tapula,
            snt = Origin.NATURAL
        )

# this is roughly equivalent to calling UpdateStandValues()
def predict(
    *,
    promote_stories: bool = True,
    **roots: Any
) -> Predict:
    p = Predict(**roots)
    if promote_stories and "trees_storie" in roots and p.promote_lower_storie:
        # TODO: strata_pvkor etc. may be updated here
        p = Predict(**{
            **roots,
            "trees_storie": [Storie.UPPER if s == Storie.LOWER else s for s in p.trees_storie]
        })
    return p

def _ccfD(predict: Predict, idx: int, d: float) -> float:
    return ccf(
        d = d,
        f = predict.trees_f[idx],
        spe = predict.trees_spe[idx],
        mty = predict.mty,
        verlt = predict.verlt,
        lake = predict.lake,
        sea = predict.sea,
        Z = predict.Z,
        dd = predict.dd
    )

def _ptalku(
    predict: Predict,
    idx: int,
    pt: PtOpt,
    age: float,
    frel: float
) -> Pt:
    return ptalku(
        pt = pt,
        spe = predict.strata_spe[idx],
        age = age,
        frel = frel,
        dd = predict.dd,
        snt = predict.strata_snt[idx],
        kiv = predict.ptkiv,
        sois = predict.ptsois,
        mty = predict.mty,
        mal = predict.mal,
        muok = predict.default_muok
    )

#---- strata attribute prediction -----------------------------------------------------

class StrataAttrs(_InitMixin):
    predict: Predict = root("predict")
    step: float = root("step")

    rdfl_skip: bool = False
    """Only for bug compatibility."""

    @property
    def num_strata(self) -> int:
        return self.predict.num_strata

    def _frel(self, idx) -> float:
        f = self.predict.strata_f[idx]
        level = self.predict.strata_level[idx]
        rltot = self.predict.level_rltot[self.predict.strata_grouping[idx]]

        if level == 1 and self.predict.F > 0:
            rltotal = min(rltot, self.predict.F)
        else:
            rltotal = max(rltot, self.predict.F)

        if (
            self.predict._elapsed(self.predict.t_perk, step=self.step) > 0
            and self.predict.t_thoit is None
            and level <= 2
        ):
            pros = frel_perk(
                f = f,
                f_level = rltot,
                f_lower = max(self.predict.level_rltot[:2]) - max(self.predict.level_rltot[:1]),
                h100_perk = self.predict.h100_perk, # type: ignore  (t_perk implies h100_perk)
                xt_perk = self.predict._elapsed(self.predict.t_perk)
            )
        else:
            pros = f / rltotal

        if (
            self.predict._elapsed(self.predict.t_thoit, step=self.step) <= 0
            and level == 1
            and (
                self.predict._elapsed(self.predict.t_synt, step=self.step) > 0
                or self.predict._elapsed(self.predict.t_perk, step=self.step) > 0
            )
        ):
            snt = self.predict.strata_snt[idx]
            xika_ero = max(self.predict.strata_agex[idx] - self.predict._elapsed(self.predict.t_synt), 0)
            comp = ikaero_comp(snt, xika_ero, self.predict._elapsed(self.predict.t_synt, step=self.step))
            if (xika_ero == 1 and snt == Origin.PLANTED) or (xika_ero == 0 and snt == Origin.NATURAL):
                rltotal = self.predict.level_rltot[-1] - comp*(self.predict.rt_synt - f)
            else:
                rltotal = self.predict.level_rltot[-1] - comp*self.predict.rt_synt
            p = f / rltotal
            if 0 < p < 1:
                pros = p

        return pros

    def _pvkor(self):
        # 0-5  pv_Da  pv_DgM  pv_Ha  pv_HgM  pv_D100  pv_H100
        # 6-11 kor_Da kor_DgM kor_Ha kor_HgM kor_D100 kor_H100
        # 12   mask
        pvkor = self.predict.strata_pvkor
        adj = np.zeros((self.predict.num_strata, 13))
        f = list(self.predict.strata_f)
        g = np.zeros(self.predict.num_strata)

        for i in range(self.predict.num_strata):
            xika = self.predict.strata_agex[i] + self.step

            if xika < 1:
                if pvkor is not None and i < pvkor.shape[0]:
                    adj[i,6:12] = pvkor[i,6:12]
                continue

            adj[i,12] = 1

            pros = self._frel(i)
            raw = _ptalku(
                self.predict,
                i,
                pt = PtOpt(f=self.predict.strata_f[i]),
                age = xika,
                frel = pros
            )

            # TODO: säädöt

            if (
                self.step == 0
                and (
                    self.predict.t_perk == self.predict.year
                    or self.predict.t_thoit == self.predict.year
                    or self.predict.t_thin == self.predict.year
                )
                and self.predict.f_small < 0.95*self.predict.rt_synt
            ):
                if self.predict.t_regen != self.predict.year and pvkor is not None and i < pvkor.shape[0]:
                    f = pvkor[i,12] * self.predict.strata_f[i]
                    rsuh = raw.f/f if f > 0 else 1
                    adj[i,6:12] = rsuh*(pvkor[i,0:6]-(raw.Da,raw.DgM,raw.Ha,raw.HgM,raw.D100,raw.H100))
                else:
                    adj[i,6:12] = raw.Da, raw.DgM, raw.Ha, raw.HgM, raw.D100, raw.H100
                    adj[i,6:12] *= -1
            elif self.predict.year == 0 and self.step == 0 and self.predict.t_thoit is None:
                pt = _ptalku(
                    self.predict,
                    i,
                    pt = PtOpt(
                        f = self.predict.strata_f[i],
                        Da = pvkor and pvkor[i,0],
                        DgM = pvkor and pvkor[i,1],
                        Ha = pvkor and pvkor[i,2],
                        HgM = pvkor and pvkor[i,3]
                    ),
                    age = xika,
                    frel = pros
                )
                adj[i,6:12] = (
                    pt.Da - raw.Da,
                    pt.DgM - raw.DgM,
                    pt.Ha - raw.Ha,
                    pt.HgM - raw.HgM,
                    pt.D100 - raw.D100,
                    pt.H100 - raw.H100
                )
            elif pvkor is not None and i < pvkor.shape[0]:
                adj[i,6:12] = pvkor[i,6:12]

            # TODO: poimintahakkuu, jalostushyöty, pkorj

            pt = _ptalku(
                self.predict,
                i,
                pt = PtOpt(
                    f = raw.f,
                    Da = raw.Da + adj[i,6],
                    DgM = raw.DgM + adj[i,7],
                    Ha = raw.Ha + adj[i,8],
                    HgM = raw.HgM + adj[i,9],
                    D100 = raw.D100 + adj[i,10],
                    H100 = raw.H100 + adj[i,11]
                ),
                age = xika,
                frel = pros
            )

            spe = self.predict.strata_spe[i]
            if spe >= 5 and (self.predict.year+self.step) != 0:
                scale = (1-spe/400)
                pt.Ha *= scale
                pt.HgM *= scale
                pt.D100 *= scale
                pt.H100 *= scale

                if pt.Ha < 1.3:
                    pt.Da = 0
                if pt.HgM < 1.3:
                    pt.DgM = 0
                if pt.H100 < 1.3:
                    pt.D100 = 0

            if xika == 1 and self.predict.strata_snt[i] != Origin.PLANTED:
                if pt.Ha < 0.1:
                    pt.Ha += 0.04
                if pt.HgM < 0.1:
                    pt.HgM += 0.05
                if pt.H100 < 0.1:
                    pt.H100 += 0.05

            f[i] = pt.f
            g[i] = pt.G
            adj[i,0:6] = pt.Da, pt.DgM, pt.Ha, pt.HgM, pt.D100, pt.H100

        self.__dict__.update(f=f, g=g, pvkor=adj)

    f = result_property(_pvkor)
    """Stem count (``1/ha``)."""

    g = result_property(_pvkor)
    """Total basal area (``m^2/ha``)."""

    pvkor = result_property(_pvkor)
    """See :attr:`metsi_grow.Predict.strata_pvkor`"""

    @property
    def da(self) -> npt.NDArray[np.float64]:
        """Arithmetic mean diameter (``cm``)."""
        return self.pvkor[:,0]

    @property
    def dgm(self) -> npt.NDArray[np.float64]:
        """Basal-area weighted mean diameter (``cm``)."""
        return self.pvkor[:,1]

    @property
    def ha(self) -> npt.NDArray[np.float64]:
        """Arithmetic mean height (``m``)."""
        return self.pvkor[:,2]

    @property
    def hgm(self) -> npt.NDArray[np.float64]:
        """Basal-area weighted mean height (``m``)."""
        return self.pvkor[:,3]

    @property
    def d100(self) -> npt.NDArray[np.float64]:
        """Arithmetic mean diameter of 100 largest trees (``cm``) by diameter."""
        return self.pvkor[:,4]

    @property
    def h100(self) -> npt.NDArray[np.float64]:
        """Arithmetic mean height of 100 largest trees (``m``) by diameter."""
        return self.pvkor[:,5]

    @cached_property
    def age13(self) -> List[float]:
        """Age at breast height (``year``)."""
        tika_lisa = [0.0] * len(Species)
        age13 = []

        for i in range(self.num_strata):
            spe = self.predict.strata_spe[i]
            xika = self.predict.strata_agex[i] + self.step
            if self.ha[i] < 1.3:
                tika_lisa[spe-1] = 0
                a = 0
            elif tika_lisa[spe-1] == 0:
                tika_lisa[spe-1] = agekri_empty(
                    spe = spe,
                    mty = self.predict.mty,
                    snt = self.predict.strata_snt[i],
                    dd = self.predict.dd,
                    verlt = self.predict.verlt,
                    hlim = 1.7,
                    alim = float("inf")
                )
                a = xika - tika_lisa[spe-1] - (self.predict.strata_level[i]-1)
            else:
                a = xika - tika_lisa[spe-1]
            age13.append(a)

        return age13

    @cached_sequence(num=num_strata.__get__)
    def ccf(self, idx) -> float:
        if self.predict.strata_agex[idx] + self.step < 1:
            return 0
        ccf = ccfi(
            spe = self.predict.strata_spe[idx],
            d = self.dgm[idx],
            h = self.hgm[idx],
            f = self.f[idx]
        )
        return ccf

    @cached_property
    def rdf(self) -> float:
        return sum(self.ccf)

    def _rdfL(self, i: int) -> float:
        rdf = self.rdf
        HgMi = self.hgm[i]
        rdfl = 0
        for j in range(self.predict.num_strata):
            HgMj = self.hgm[j]
            if HgMj >= HgMi:
                rdfl += self.ccf[j] / (2*HgMi/HgMj)
                rdfl = min(rdfl, rdf)
                if rdfl == rdf:
                    rdfl -= self.ccf[i]/2
        return rdfl

    @cached_property
    def f_thinned(self) -> List[float]:
        """Stem count after stratum-level thinning (``1/ha``)"""
        rdf = self.rdf
        ft = list(self.f)
        surv = 0

        for i in self.predict.strata_order:
            f = self.f[i]
            HgMi = self.hgm[i]
            if HgMi > 0:
                rdfl = self._rdfL(i)
                if rdfl > 0.3 and not self.rdfl_skip:
                    if self.step == 0:
                        continue
                    if (
                        self.predict.strata_type[i] == SaplingType.INFEASIBLE
                        or self.predict.strata_spe[i] >= 8
                    ):
                        DgMi = self.dgm[i]
                        surv = ptsurvjs(
                            spe = self.predict.strata_spe[i],
                            rdfl = rdfl,
                            dk = dk(DgMi) if HgMi > 3 else dkjs_small(HgMi),
                            step = self.step
                        )
                        f *= surv
                        if f < 0.5:
                            f = 0

            if rdf > 1.0 and surv == 0:
                f /= rdf

            ft[i] = f

            # TODO: poimintahakkuu

        return ft

#---- natural processes ----------------------------------------

class EvolvedStorie(_InitMixin):
    evolve: "Evolve" = root("evolve")
    which: Storie = root("which")

    @property
    def predict(self) -> Predict:
        return self.evolve.predict

    @cached_property
    def thin_fratio(self) -> List[float]:
        """Relative density of the storie."""
        dg = self.predict.storie[self.which].dg
        f = self.predict.storie[self.which].f
        if self.predict.alr == SoilCategoryVMI.MINERAL:
            if self.which <= 2:
                return self_thin_mineral_12(
                    dg = dg,
                    f = f,
                    hg = [self.evolve.hg3[s,] for s in Species],
                    rdf = [self.evolve.rdf2[s,] for s in Species],
                    rdftot = self.evolve.rdf2[Species],
                    hd50_4 = [self.predict.hd50[Species(s)] for s in range(1,5)]
                )
            else:
                return self_thin_mineral_34(
                    dg = dg,
                    f = f,
                    hd50_4 = [self.predict.hd50[Species(s)] for s in range(1,5)]
                )
        else:
            if self.which <= 2:
                return self_thin_peat_12(
                    dg = dg,
                    f = f,
                    hg = [self.evolve.hg3[s,] for s in Species],
                    rdf = [self.evolve.rdf2[s,] for s in Species],
                    rdftot = self.evolve.rdf2[Species]
                )
            else:
                return self_thin_peat_34(
                    dg = dg,
                    f = f
                )

    @cached_property
    def thin_cratio(self) -> float:
        """Cumulative max ratio."""
        rs = [0.0] * len(Species)
        for s in range(self.which+1,Storie.RETENTION+1):
            for i,r in enumerate(self.evolve.storie[Storie(s)].thin_fratio):
                rs[i] += r
        return max(rs)

    @cached_mapping
    def thin_uratio(self, spe: Species) -> float:
        """Relative density including upper stories."""
        r = self.thin_fratio[spe-1]
        if r > 1.0001:
            return r + self.thin_cratio
        else:
            return 1

class Evolve(_InitMixin):
    predict: Predict = root("predict")
    step: float = 5.0
    tree_death: bool = True
    self_thinning: bool = True

    @property
    def num_trees(self) -> int:
        return self.predict.num_trees

    @property
    def num_strata(self) -> int:
        return self.predict.num_strata

    @property
    def delta(self) -> float:
        return self.step/5.0

    @cached_mapping
    def storie(self, which: Storie) -> EvolvedStorie:
        return EvolvedStorie(evolve=self, which=which)

    @cached_sequence(num=num_trees.__get__)
    def trees_v1b(self, i) -> float:
        """Stem-curve volume after a 5 year time step (stage 1b)."""
        h = self.predict.trees_h[i] + self.trees_ih1b[i]
        d = self.predict.trees_dnz[i] + self.trees_id1b[i]
        spe = self.predict.trees_spe[i]
        # crk works just fine for spe>4. why this check? who knows..
        if spe > 4:
            spe = Species.PINE if spe == 8 else Species.DOWNY_BIRCH
        # why use a different volume model here? who knows..
        return crkv0(
            crk = ucrkdbh(spe=spe, h=h, hmit=0, d=d),
            h = max(hkan(spe, h, d), 0.1)
        ) / 1000

    @cached_property
    def V1b(self) -> float:
        """volume after stage 1b growth step."""
        return dot(self.predict.trees_f, self.trees_v1b)

    @cached_property
    def iV1b(self) -> float:
        """volume growth during stage 1b growth step."""
        return self.V1b - self.predict.V

    @cached_property
    def hdom100s1(self) -> float:
        """:attr:`metsi_grow.Predict.hdom100` after stage 1 growth."""
        hdom100, = hdom100_spe(
            h = [self.predict.trees_h[i] + self.trees_ih1[i] for i in range(self.num_trees)],
            f = self.predict.trees_f,
            d = [self.predict.trees_dnz[i] + self.trees_id1[i] for i in range(self.num_trees)],
            storie = self.predict.trees_storie,
            spe = self.predict.trees_spe,
            choose = (Species, ),
            grow = self.predict.growing_storie
        )
        return hdom100

    @cached_sequence(num=num_trees.__get__)
    def trees_ccf2(self, i) -> float:
        """:attr:`trees_ccf <metsi_grow.Predict.trees_ccf>` after stage 2 growth."""
        return _ccfD(self.predict, i, self.predict.trees_dnz[i]+self.trees_id2[i])

    @cached_mapping
    def rdf2(self, spe: Container[Species]) -> float:
        """:attr:`rdf <metsi_grow.Predict.rdf>` after stage 2 growth."""
        return sum(ccf for ccf,s in zip(self.trees_ccf2, self.predict.trees_spe) if s in spe)

    @cached_mapping
    def trees_ccfL2(self, spe: Container[Species]) -> List[float]:
        """:attr:`trees_ccfL <metsi_grow.Predict.trees_ccfL>` after stage 2 growth."""
        ccfL, = ccfL_spe(
            prio = [self.predict.trees_dnz[i]+self.trees_id2[i] for i in range(self.num_trees)],
            ccf = self.trees_ccf2,
            spe = self.predict.trees_spe,
            choose = (spe, )
        )
        return ccfL

    @cached_sequence(num=num_trees.__get__)
    def trees_d3(self, i) -> float:
        """:attr:`trees_d <metsi_grow.Predict.trees_d>` after growth."""
        return self.predict.trees_dnz[i] + self.trees_id[i]

    @cached_sequence(num=num_trees.__get__)
    def trees_h3(self, i) -> float:
        """:attr:`trees_h <metsi_grow.Predict.trees_h>` after growth."""
        return self.predict.trees_h[i] + self.trees_ih[i]

    @cached_property
    def dg3(self) -> float:
        """:attr:`dg <metsi_grow.Predict.dg>` after growth."""
        return dg(self.trees_d3, self.predict.trees_f)

    @cached_mapping
    def hg3(self, spe: Container[Species]) -> float:
        """:attr:`hg <metsi_grow.Predict.hg>` after growth."""
        return xg_subseq(
            x = self.trees_h3,
            d = self.trees_d3,
            f = self.predict.trees_f,
            subseq = (sp in spe and st < Storie.OVER
                      for sp,st in zip(self.predict.trees_spe, self.predict.trees_storie))
        )

    @cached_property
    def ddomjs3(self) -> float:
        """:attr:`ddomj <metsi_grow.Predict.ddomj>` after growth."""
        return xdomj(
            x = self.trees_d3,
            f = self.predict.trees_f,
            d = self.trees_d3,
            dlim = self.dg3
        )

    #-- growth --------------------
    # stage 1b: raw 5-year large-tree model grow step (BasalAreaGrowth/HeightGrowth)
    # stage 1: raw 5-year grow step (stage1b or SaplisGroth)
    # stage 2: stage 1 + fertilization effect
    # stage 3: stage 2 + interpolation

    #-- growth: stage 1 --------------------

    @cached_sequence(num=num_trees.__get__)
    def trees_id1b(self, idx) -> float:
        """Stage 1b diameter growth."""
        if self.predict.alr == SoilCategoryVMI.MINERAL:
            return ba2d(self.predict.trees_ba[idx]+self.trees_ig1b[idx]) - self.predict.trees_dnz[idx]
        spe = self.predict.trees_spe[idx]
        hdom100 = self.predict.hdom100[Species]
        if hdom100 == 0 and self.predict.trees_storie[idx] > Storie.UPPER:
            hdom100 = self.predict.storie[self.predict.trees_storie[idx]].h100
        if hdom100 == 0:
            hdom100 = self.predict.trees_h[idx]
        if spe == Species.PINE:
            id = id5_suo_manty(
                d = self.predict.trees_dnz[idx],
                baL = self.predict.trees_baL[Species][idx],
                G = self.predict.G[Species],
                hdom100 = hdom100,
                dd = self.predict.dd,
                mal = self.predict.mal,
                oji = self.predict.oji,
                tkg = self.predict.tkg,
                sty = self.predict.sty,
                rimp = self.predict.rimp,
                dr = self.predict._elapsed(self.predict.t_rdrain),
                dnm = self.predict._elapsed(self.predict.t_ndrain),
                pdr = self.predict.pdr,
                xt_thin = self.predict._elapsed(self.predict.t_thin)
            )
        elif spe == Species.SPRUCE:
            id = id5_suo_kuusi(
                d = self.predict.trees_dnz[idx],
                baLku = self.predict.trees_baL[Species.SPRUCE, ][idx],
                G = self.predict.G[Species],
                hdom100 = hdom100,
                dd = self.predict.dd,
                mal = self.predict.mal,
                Z = self.predict.Z,
                oji = self.predict.oji,
                tkg = self.predict.tkg,
                dr = self.predict._elapsed(self.predict.t_rdrain),
                dnm = self.predict._elapsed(self.predict.t_ndrain),
                xt_thin = self.predict._elapsed(self.predict.t_thin)
            )
        else:
            return id5_suo_koivu(
                d = self.predict.trees_dnz[idx],
                baLlehti = self.predict.trees_baL[
                    Species.SILVER_BIRCH, Species.DOWNY_BIRCH,
                    Species.ASPEN, Species.GRAY_ALDER,
                    Species.BLACK_ALDER, Species.DECIDUOUS
                ][idx],
                G = self.predict.G[Species],
                hdom100 = hdom100,
                dd = self.predict.dd,
                mal = self.predict.mal,
                Z = self.predict.Z,
                oji = self.predict.oji,
                tkg = self.predict.tkg,
                dr = self.predict._elapsed(self.predict.t_rdrain),
                dnm = self.predict._elapsed(self.predict.t_ndrain),
                xt_thin = self.predict._elapsed(self.predict.t_thin),
                xt_fert = self.predict._elapsed(self.predict.t_fert)
            )
        # jalostushyöty vain männylle ja kuuselle.
        if self.predict.trees_snt[idx] > Origin.NATURAL:
            id *= 1 + self.predict.jd
        return id

    @cached_sequence(num=num_trees.__get__)
    def trees_ig1b(self, idx) -> float:
        """Stage 1b basal area growth."""
        if self.predict.alr > SoilCategoryVMI.MINERAL:
            return d2ba(self.predict.trees_dnz[idx] + self.trees_id1b[idx]) - self.predict.trees_ba[idx]
        return ig5_figu(
            spe = self.predict.trees_spe[idx],
            d = self.predict.trees_dnz[idx],
            h = self.predict.trees_h[idx],
            rdfl = self.predict.trees_ccfL[Species][idx],
            rdflma = self.predict.trees_ccfL[Species.PINE,][idx],
            rdflku = self.predict.trees_ccfL[Species.SPRUCE,][idx],
            rdfl_lehti = self.predict.trees_ccfL[
                Species.SILVER_BIRCH, Species.DOWNY_BIRCH,
                Species.ASPEN, Species.GRAY_ALDER,
                Species.BLACK_ALDER, Species.DECIDUOUS
            ][idx],
            cr = self.predict.trees_cr[idx],
            crkor = self.predict.trees_cr[idx] - self.predict.trees_cr_raw[idx],
            snt = self.predict.trees_snt[idx],
            mty = self.predict.mty,
            mal = self.predict.mal,
            dd = self.predict.dd,
            rdf = self.predict.rdf[Species],
            rdfma = self.predict.rdf[Species.PINE,],
            rdfku = self.predict.rdf[Species.SPRUCE,],
            rdf_lehti = self.predict.rdf[
                Species.SILVER_BIRCH, Species.DOWNY_BIRCH,
                Species.ASPEN, Species.GRAY_ALDER,
                Species.BLACK_ALDER, Species.DECIDUOUS
            ]
        ) / (100**2)

    @cached_sequence(num=num_trees.__get__)
    def trees_ih1b(self, idx) -> float:
        """Stage 1b height growth."""
        spe = self.predict.trees_spe[idx]
        if self.predict.alr == SoilCategoryVMI.MINERAL:
            return ih5_fihu(
                spe = spe,
                d = self.predict.trees_dnz[idx],
                h = self.predict.trees_h[idx],
                rdfl = self.predict.trees_ccfL[Species][idx],
                rdflma = self.predict.trees_ccfL[Species.PINE,][idx],
                rdflku = self.predict.trees_ccfL[Species.SPRUCE,][idx],
                cr = self.predict.trees_cr[idx],
                crkor = self.predict.trees_cr[idx] - self.predict.trees_cr_raw[idx],
                ig5 = self.trees_ig1b[idx],
                mty = self.predict.mty,
                mal = self.predict.mal,
                dd = self.predict.dd,
                hdomj = self.predict.hdomj,
                jd = self.predict.jd
            )
        else:
            hdom100 = self.predict.hdom100[Species]
            if hdom100 == 0 and self.predict.trees_storie[idx] > Storie.UPPER:
                hdom100 = self.predict.storie[self.predict.trees_storie[idx]].h100
            # for whatever reason this next check doesn't exist in id5,
            # otherwise the h100 logic matches.
            if hdom100 == 0:
                hdom100 = self.predict.st12_h100
            if hdom100 == 0:
                hdom100 = self.predict.trees_h[idx]
            if spe == Species.PINE:
                ih = ih5_suo_manty(
                    d = self.predict.trees_dnz[idx],
                    baL = self.predict.trees_baL[Species][idx],
                    G = self.predict.G[Species],
                    G_koivu = self.predict.G[Species.SILVER_BIRCH, Species.DOWNY_BIRCH],
                    hdom100 = hdom100,
                    dd = self.predict.dd,
                    mal = self.predict.mal,
                    tkg = self.predict.tkg,
                    dnm = self.predict._elapsed(self.predict.t_ndrain),
                    pdr = self.predict.ojik == DitchCondition.GOOD
                )
            elif spe == Species.SPRUCE:
                ih = ih5_suo_kuusi(
                    d = self.predict.trees_dnz[idx],
                    baLku = self.predict.trees_baL[Species.SPRUCE, ][idx],
                    hdom100 = hdom100,
                    dd = self.predict.dd,
                    mal = self.predict.mal,
                    tkg = self.predict.tkg,
                    dr = self.predict._elapsed(self.predict.t_rdrain),
                    dnm = self.predict._elapsed(self.predict.t_ndrain),
                )
            else:
                ih = ih5_suo_koivu(
                    d = self.predict.trees_dnz[idx],
                    baLlehti = self.predict.trees_baL[
                        Species.SILVER_BIRCH, Species.DOWNY_BIRCH,
                        Species.ASPEN, Species.GRAY_ALDER,
                        Species.BLACK_ALDER, Species.DECIDUOUS
                    ][idx],
                    dg = self.predict.dgdom,
                    G = self.predict.G[Species],
                    G_manty = self.predict.G[Species.PINE, ],
                    F = self.predict.F,
                    hdom100 = hdom100,
                    dd = self.predict.dd,
                    Z = self.predict.Z,
                    mal = self.predict.mal,
                    tkg = self.predict.tkg,
                    dr = self.predict._elapsed(self.predict.t_rdrain),
                    dnm = self.predict._elapsed(self.predict.t_ndrain),
                    xt_thin = self.predict._elapsed(self.predict.t_thin),
                    xt_fert = self.predict._elapsed(self.predict.t_fert)
                )
            if ih <= 0:
                return 0.0001
            ih = ih5adj(
                ih5 = ih,
                G = self.predict.G[Species],
                dd = self.predict.dd,
                mal = self.predict.mal,
                oji = self.predict.oji,
                tkg = self.predict.tkg
            )
            if self.predict.trees_snt[idx] > Origin.NATURAL and spe in (Species.PINE, Species.SPRUCE):
                ih *= 1 + self.predict.jh
            return ih

    @cached_sequence(num=num_trees.__get__)
    def trees_id1(self, idx) -> float:
        """Stage 1 diameter growth."""
        h = self.predict.trees_h[idx]
        if h < 1.3:
            ih = self.trees_ih1[idx]
            if h + ih < 1.3:
                return 0
            return id_init(
                spe = self.predict.trees_spe[idx],
                h = h,
                ih5 = ih,
                rdfl = self.predict.trees_ccfL[Species][idx],
                rdflma = self.predict.trees_ccfL[Species.PINE,][idx],
                rdflku = self.predict.trees_ccfL[Species.SPRUCE,][idx],
                rdfl_lehti = self.predict.trees_ccfL[
                    Species.SILVER_BIRCH, Species.DOWNY_BIRCH,
                    Species.ASPEN, Species.GRAY_ALDER,
                    Species.BLACK_ALDER, Species.DECIDUOUS
                ][idx],
                cr = self.predict.trees_cr[idx],
                crkor = self.predict.trees_cr[idx] - self.predict.trees_cr_raw[idx],
                snt = self.predict.trees_snt[idx],
                mty = self.predict.mty,
                mal = self.predict.mal,
                dd = self.predict.dd,
                rdf = self.predict.rdf[Species],
                rdfma = self.predict.rdf[Species.PINE,],
                rdfku = self.predict.rdf[Species.SPRUCE,],
                rdf_lehti = self.predict.rdf[
                    Species.SILVER_BIRCH, Species.DOWNY_BIRCH,
                    Species.ASPEN, Species.GRAY_ALDER,
                    Species.BLACK_ALDER, Species.DECIDUOUS
                ],
                jd = self.predict.jd,
                step = self.step
            )
        else:
            return self.trees_id1b[idx]

    @cached_sequence(num=num_trees.__get__)
    def trees_ig1(self, idx) -> float:
        """Stage 1 basal area growth."""
        if self.predict.trees_h[idx] < 1.3:
            return d2ba(self.predict.trees_dnz[idx] + self.trees_id1[idx]) - self.predict.trees_ba[idx]
        else:
            return self.trees_ig1b[idx]

    @cached_sequence(num=num_trees.__get__)
    def trees_ih1(self, idx) -> float:
        """Stage 1 height growth."""
        if self.predict.trees_h[idx] < 1.3:
            # unlike ba-growth, h-growth for saplings isn't interpolated here
            # (no, the `step` parameter doesn't control interpolation)
            return hincu(
                spe = self.predict.trees_spe[idx],
                age = self.predict.trees_age[idx],
                h = self.predict.trees_h[idx],
                snt = self.predict.trees_snt[idx],
                mty = self.predict.mty,
                dd = self.predict.dd,
                G = self.predict.G[Species],
                step = self.step
            )
        else:
            return self.trees_ih1b[idx]

    #-- growth: stage 2 --------------------

    @cached_mapping
    def fv(self, spe: Species) -> float:
        """Fertilization effect on volume growth."""
        if self.predict.num_fert == 0:
            return 0
        if self.predict.alr == SoilCategoryVMI.MINERAL:
            if self.iV1b == 0:
                return 0
            # TODO: typpihäviöt puuttuu
            iv = self.predict.fert_level * iv_rf_mot(
                mty = self.predict.mty,
                dd = self.predict.dd,
                year = self.predict.year,
                age = self.predict.st12_age100,
                F = self.predict.F,
                frma = int(spe in (Species.PINE, Species.CONIFEROUS)),
                frku = int(spe == Species.SPRUCE),
                years = self.predict.fert_year[:3],
                amt = self.predict.fert_amt[:3],
                type = self.predict.fert_type[:3],
                p = self.predict.fert_p[:3],
                step = round(self.step)
            )
            return 5.0 * iv/self.iV1b
        elif self.predict.alr == SoilCategoryVMI.PEAT_PINE:
            iv = iv_fert(
                mty = self.predict.mty,
                dd = self.predict.dd,
                pd = self.predict.pd,
                hdom = self.hdom100s1,
                N0 = self.predict.fert_N0[-1],
                V0 = self.predict.fert_V0[-1],
                xt_fert = self.predict._elapsed(self.predict.fert_year[-1]) + self.step/2,
                xt_basicfert = 99,
                type = self.predict.fert_type[-1],
                tkg = self.predict.tkg
            )
            if spe == Species.PINE:
                return iv
            elif spe in (Species.SILVER_BIRCH, Species.DOWNY_BIRCH):
                return 0.75 * iv
            else:
                return 0.5 * iv
        else:
            return 0

    @cached_mapping
    def fh(self, spe: Species) -> float:
        """Fertilization effect on height growth."""
        if self.fv[spe] == 0:
            return 0
        return ih_hpros(
            alr = self.predict.alr,
            dd = self.predict.dd,
            spe = spe,
            ccf = self.predict.rdf[Species],
            ccfL = self.predict.rdf[Species]/2,
            vpros = self.fv[spe]
        )

    def _stage2_fert(self, idx: int):
        if self.predict.num_fert > 0:
            spe = self.predict.trees_spe[idx]
            if self.predict.alr == SoilCategoryVMI.MINERAL:
                id, ih = fert_a(
                    spe = spe,
                    d = self.predict.trees_dnz[idx],
                    h = self.predict.trees_h[idx],
                    id5 = self.trees_id1[idx],
                    ih5 = self.trees_ih1[idx],
                    fh = self.fh[spe],
                    fv = self.fv[spe]
                )
            else:
                id = fert_b(
                    spe = spe,
                    d = self.predict.trees_dnz[idx],
                    h = self.predict.trees_h[idx],
                    id5 = self.trees_id1[idx],
                    ih5 = self.trees_ih1[idx],
                    fh = self.fh[spe],
                    fv = self.fv[spe]
                )
                ih = self.trees_ih1[idx]
        else:
            # TODO: could make this just patch the lists directly as an optimization,
            # since now they will just be copied.
            id = self.trees_id1[idx]
            ih = self.trees_ih1[idx]
        self.trees_id2[idx] = id
        self.trees_ih2[idx] = ih

    @cached_sequence(num=num_trees.__get__)
    def trees_id2(self, idx) -> float:
        """Stage 2 diameter growth."""
        self._stage2_fert(idx)
        return self.trees_id2[idx]

    @cached_sequence(num=num_trees.__get__)
    def trees_ih2(self, idx) -> float:
        """Stage 2 height growth."""
        self._stage2_fert(idx)
        return self.trees_ih2[idx]

    #-- growth: stage 3 --------------------

    @cached_sequence(num=num_trees.__get__)
    def trees_id(self, idx) -> float:
        """Diameter growth (``cm``)."""
        if self.trees_h3[idx] < 1.3:
            return 0
        if self.predict.trees_h[idx] < 1.3 and self.predict.alr == SoilCategoryVMI.MINERAL:
            return self.trees_id2[idx]
        # note: small trees are interpolated inside the model, but big trees only
        # after updating competition.
        # however! on peatland the small-tree-is-already-interpolated condition isn't
        # checked, so we re-interpolate them, basically reducing growth twice.
        # this looks like a bug, but it's replicated here for compatiblity.
        return self.delta * self.trees_id2[idx]

    @cached_sequence(num=num_trees.__get__)
    def trees_ig(self, idx) -> float:
        """Basal area growth (``m^2``)."""
        return d2ba(self.trees_d3[idx]) - self.predict.trees_ba[idx]

    @cached_sequence(num=num_trees.__get__)
    def trees_ih(self, idx) -> float:
        """Height growth (``m``)."""
        # the interpolation condition here is the same as in `trees_id`,
        # however since h-growth isn't interpolated in the model,
        # it has the opposite effect: interpolated saplings have the correct
        # behavior while skipped saplings have uninterpolated growth.
        if self.predict.trees_h[idx] < 1.3 and self.predict.alr == SoilCategoryVMI.MINERAL:
            return self.trees_ih2[idx]
        return self.delta * self.trees_ih2[idx]

    #-- death / tree level ----------------------------------------

    @cached_sequence(num=num_trees.__get__)
    def trees_sp(self, idx) -> float:
        """Tree-level survival probability."""
        spe = self.predict.trees_spe[idx]
        if self.predict.alr == SoilCategoryVMI.MINERAL:
            sp = jsdeath_interp(
                spe = spe,
                d = self.trees_d3[idx],
                id = self.trees_id[idx],
                rdfl = self.trees_ccfL2[Species][idx],
                step = self.step
            )
        else:
            if spe == Species.SPRUCE:
                sp = jsdeath_kuusi(
                    d = self.trees_d3[idx],
                    rdfl = self.trees_ccfL2[Species][idx],
                    step = self.step
                )
            elif spe in (Species.PINE, Species.CONIFEROUS):
                sp = pmodel3a_suo_manty(
                    d = self.predict.trees_dnz[idx],
                    baL = self.predict.trees_baL[Species][idx],
                    G = self.predict.G[Species],
                    Grel_lehti = self.predict.Grel_lehti,
                    dg = self.predict.dg,
                    step = self.step
                )
            else:
                sp = bmodel3_suo_koivu(
                    d = self.predict.trees_dnz[idx],
                    baL = self.predict.trees_baL[Species][idx],
                    G = self.predict.G[Species],
                    Grel_manty = self.predict.Grel_manty,
                    dd = self.predict.dd,
                    step = self.step
                )
        spf = famort(
            spe = spe,
            age13 = self.predict.trees_age13[idx] + self.step,
            dd = self.predict.dd
        )
        return sp*spf

    #-- death / self thinning ----------------------------------------
    # this is totally uninterpolated

    @cached_property
    def trees_thinsp(self) -> npt.NDArray[np.float64]:
        """Self-thinning survival probability."""
        N = np.zeros((4,9))
        S = np.zeros((4,9))

        fs = self.predict.trees_f
        if self.tree_death:
            fs = [f*p for f,p in zip(fs, self.trees_sp)]

        for i in range(self.num_trees):
            storie = self.predict.trees_storie[i]
            if storie == Storie.NONE:
                continue
            spe = self.predict.trees_spe[i]
            N[storie-1,spe-1] += fs[i]
            #s = 1 - self_thin_tree(self.ddomjs3, self.predict.trees_dnz[i])
            s = 1
            k = 1 - 1/self.storie[storie].thin_uratio[spe]
            S[storie-1,spe-1] += fs[i]*s*k

        p = np.ones(self.num_trees)
        for i in range(self.num_trees):
            storie = self.predict.trees_storie[i]
            if storie == Storie.NONE:
                continue
            spe = self.predict.trees_spe[i]
            if S[storie-1,spe-1] == 0:
                continue
            k = 1 - 1/self.storie[storie].thin_uratio[spe]
            #s = 1 - self_thin_tree(self.ddomjs3, self.predict.trees_dnz[i])
            s = 1
            kk = k * N[storie-1,spe-1] / S[storie-1,spe-1]
            p[i] = 1 - kk*k*s

        return p

    #-- death ----------------------------------------

    @cached_property
    def trees_if(self) -> Reals:
        """Stem count change (``1/ha``)."""
        p = np.ones(self.num_trees)
        if self.tree_death:
            p *= self.trees_sp
        if self.self_thinning:
            p *= self.trees_thinsp
        df = -(1-p)*self.predict.trees_f # type: ignore
        if self.self_thinning and self.step < 5:
            if self.tree_death:
                # this is a bit hacky: we don't want to interpolate those trees
                # that tree-level death already deleted.
                df[self.predict.trees_f*np.array(self.trees_sp)>0.15] *= self.delta # type: ignore
            else:
                df *= self.delta
        return df

class CreateTrees(_InitMixin):
    predict: Predict = root("predict")
    idx: Ints = root("idx")
    step: float = root("step")
    flim: float = root("flim")

    @cached_property
    def storie(self) -> Storie:
        """Storie of created trees."""
        return Storie.LOWER if self.predict.st12_h100 > 10 else Storie.UPPER

    @cached_property
    def strata_attrs(self) -> StrataAttrs:
        return self.predict.evolve_strata(self.step)

    @cached_property
    def _level_rltot(self) -> List[float]:
        return prefixsum_level(self.strata_attrs.f_thinned, self.predict.strata_grouping)

    # we use different logic here. don't ask me.
    def _frel(self, idx) -> float:
        f = self.strata_attrs.f_thinned[idx]
        if self.predict.strata_level[idx] >= 2:
            return f / self._level_rltot[self.predict.strata_grouping[idx]]
        snt = self.predict.strata_snt[idx]
        xika_ero = max(self.predict.strata_agex[idx] - self.predict._elapsed(self.predict.t_synt), 0)
        comp = ikaero_comp(snt, xika_ero, self.predict._elapsed(self.predict.t_synt, step=self.step))
        if (xika_ero == 1 and snt == Origin.PLANTED) or (xika_ero == 0 and snt == Origin.SEEDED):
            rltotal = self._level_rltot[-1] - comp*(self.predict.rt_synt - f)
        else:
            rltotal = self._level_rltot[-1] - comp*self.predict.rt_synt
        pros = f / rltotal
        if 0 < pros < 1:
            return pros
        else:
            return f / self._level_rltot[self.predict.strata_grouping[idx]]

    def _create(self):
        self.__dict__.update(src=[], f=[], d=[], h=[])

        if (self.predict.strata_g is not None) and (self.predict.strata_pvkor is not None):
            sf = self.predict.strata_f
            sg = self.predict.strata_g
            pv = self.predict.strata_pvkor
        else:
            sf = self.strata_attrs.f_thinned
            sg = self.strata_attrs.g
            pv = self.strata_attrs.pvkor

        for idx in self.idx:
            f = sf[idx]
            if f < self.flim:
                continue

            spe = self.predict.strata_spe[idx]
            level = self.predict.strata_level[idx]
            g = sg[idx]
            fi, gi = f, g
            da, dgm, ha, hgm = pv[idx,0:4]
            hdom = pv[idx,5]
            dgi = dgm
            ddom = self.predict.ddom100[Species] if (spe == self.predict.spedom and level == 1) else 0
            age = self.predict.strata_agex[idx] + self.step

            if min(f, g, da, dgm, ha, hgm, ddom, hdom) == 0:
                pros = self._frel(idx)
                pt = _ptalku(
                    self.predict,
                    idx,
                    pt = PtOpt(f=self.strata_attrs.f_thinned[idx]),
                    age = age,
                    frel = pros
                )

                if (
                    spe == self.predict.spedom
                    and self.predict.prt >= Origin.SEEDED
                    and max(self.predict.jd, self.predict.jh) > 0
                ):
                    ptopt = PtOpt(f=pt.f, DgM=pt.DgM, Ha=pt.Ha, HgM=pt.HgM)
                    if self.predict.strata_snt[idx] >= Origin.SEEDED:
                        ptopt.DgM *= 1 + self.predict.jd     # type: ignore
                        ptopt.Ha *= 1 + self.predict.jh      # type: ignore
                        ptopt.HgM *= 1 + self.predict.jh     # type: ignore

                    pt = _ptalku(self.predict, idx, pt=ptopt, age=age, frel=pros)
                    # TODO: poimintahakkuu

                    kor = self.predict.strata_pvkor
                    if kor is not None:
                        pt.Da += kor[idx,6]
                        pt.DgM += kor[idx,7]
                        pt.Ha += kor[idx,8]
                        pt.HgM += kor[idx,9]
                        pt.D100 += kor[idx,10]
                        pt.H100 += kor[idx,11]

                    pt.G = 0
                    pt = _ptalku(
                        self.predict,
                        idx,
                        pt = PtOpt(**dataclasses.asdict(pt)),
                        age = age,
                        frel = pros
                    )

                if spe >= 5:
                    scale = (1-spe/400)
                    pt.Ha *= scale
                    pt.HgM *= scale
                    pt.D100 *= scale
                    pt.H100 *= scale

                f, g, da, dgm, ha, hgm = pt.f, pt.G, pt.Da, pt.DgM, pt.Ha, pt.HgM
                ddom, hdom = pt.D100, pt.H100

            n = ndistrib(f)
            if spe == self.predict.spedom:
                n *= 2

            fdh = rakenne(
                f = f,
                fi = fi,
                frel = f / self.predict.F,
                g = g,
                gi = gi,
                ha = ha,
                hgm = hgm,
                hdom = hdom,
                da = da,
                dgm = dgm,
                ddom = ddom,
                dgi = dgi,
                age = age,
                spe = spe,
                storie = self.storie,
                snt = self.predict.strata_snt[idx],
                type = self.predict.strata_type[idx],
                n = n,
                dd = self.predict.dd
            )

            self.src.extend(idx for _ in range(len(fdh.f)))
            self.f.extend(fdh.f)
            self.d.extend(fdh.d)
            self.h.extend(fdh.h)

            # motin bugi (?): tunnukset vanhoja ensimmäisellä CreateNewTrees()-kutsulla.
            sf, sg, pv = self.strata_attrs.f_thinned, self.strata_attrs.g, self.strata_attrs.pvkor

    src: List[int] = result_property(_create)
    """Source stratum index for each created tree."""

    f: List[float] = result_property(_create)
    """:attr:`stem count <metsi_grow.Predict.trees_f>` for created trees (``1/ha``)."""

    d: List[float] = result_property(_create)
    """:attr:`breast height diameter <metsi_grow.Predict.trees_d>` for created trees (``cm``)."""

    h: List[float] = result_property(_create)
    """:attr:`height <metsi_grow.Predict.trees_h>` for created trees (``m``)."""

    @property
    def num_trees(self) -> int:
        """Number of created trees."""
        return len(self.f)

#---- regeneration prediction ----------------------------------------

class Regenerate(_InitMixin):
    predict: Predict = root("predict")
    tapula: Tapula = root("tapula")
    snt: Origin = root("snt")
    vspe: Optional[Species] = None
    vf: Optional[float] = None
    surv: Optional[float] = None
    mood: bool = False

    @property
    def viti(self) -> float:
        return (self.vf or 0) * (self.surv or 0)

    @cached_property
    def agekri_empty(self) -> float:
        """Age at which trees should be generated from the created strata."""
        return agekri_empty(
            spe = self.predict.spedom,
            mty = self.predict.mty,
            snt = self.snt,
            dd = self.predict.dd,
            verlt = self.predict.verlt
        )

    def _regenerate(self):
        self.__dict__.update(t0=[], f=[], level=[], spe=[], type=[])

        level = max(self.predict.strata_level, default=0) + 1

        syn = synt(
            mty = self.predict.mty,
            alr = self.predict.alr,
            snt = self.snt,
            dd = self.predict.dd,
            F = self.predict.F,
            G_seed = self.predict.G_seed,
            t_muok = self.predict._elapsed(self.predict.t_muok),
            muok = self.predict.muok,
            tspe = self.tapula.tspe,
            yer = self.tapula.yer,
            plerc = self.tapula.plerc,
            f_vilj = self.viti,
            surv = self.surv or 0,
            mood = self.mood
        )

        if self.viti > 0 and self.vspe:
            if syn.yrt[self.vspe-1] < 50:
                syn.yrt[self.vspe-1] = 0
            if syn.ykt[self.vspe-1] < 50:
                syn.ykt[self.vspe-1] = 0

            self.t0.append(self.predict.year + (0 if self.snt < Origin.PLANTED else -1))
            self.f.append(self.viti)
            self.level.append(level)
            self.spe.append(self.vspe)
            self.type.append(SaplingType.CULTIVATED)
            level += 1

        fkpsu = [0.0] * len(Species)
        fklsu = [0.0] * len(Species)
        for sp,f,typ in zip(self.predict.strata_spe, self.predict.strata_f, self.predict.strata_type):
            if typ == SaplingType.INFEASIBLE:
                fklsu[sp-1] += f
            else:
                fkpsu[sp-1] += f

        for sp in Species:
            fkp = syn.ykt[sp-1]

            # HUOM: ehto vastaa fortrania, onkohan tarkoituksellinen?
            if self.viti > 0:
                fkp -= fkpsu[sp-1]
            if sp == self.vspe:
                fkp -= self.viti
            if fkp > 0:
                self.t0.append(self.predict.year)
                self.f.append(fkp)
                self.level.append(level)
                self.spe.append(sp)
                self.type.append(SaplingType.NATURAL)

            fkl = syn.yrt[sp-1] - syn.ykt[sp-1] - fklsu[sp-1]
            if fkl > 0:
                self.t0.append(self.predict.year)
                self.f.append(fkl)
                self.level.append(level)
                self.spe.append(sp)
                self.type.append(SaplingType.INFEASIBLE)

    t0: List[float] = result_property(_regenerate)
    """Birth year of the strata (see :attr:`metsi_grow.Predict.strata_t0`)."""

    f: List[float] = result_property(_regenerate)
    """Stem count of the strata (see :attr:`metsi_grow.Predict.strata_f`)."""

    level: List[int] = result_property(_regenerate)
    """Level of the strata (see :attr:`metsi_grow.Predict.strata_level`)."""

    spe: List[Species] = result_property(_regenerate)
    """Species of the strata (see :attr:`metsi_grow.Predict.strata_spe`)."""

    type: List[SaplingType] = result_property(_regenerate)
    """Type of the strata (see :attr:`metsi_grow.Predict.strata_type`)."""
