
from lukefi.metsi.data.model import ForestStand
from functools import cached_property
from lukefi.metsi.forestry.naturalprocess.metsi_grow.chain import Predict, predict, Species, LandUseCategoryVMI, SiteTypeVMI, \
    SoilCategoryVMI, TaxClass, TaxClassReduction, Origin, Storie
import lukefi.metsi.domain.natural_processes.grow_metsi as domain_gm

class MetsiGrowPredictor(Predict):
    """
    Extend metsi_grow.Predict to interface ForestStand & ReferenceTree data.
    """

    def __init__(self, stand: ForestStand):
        # store stand for property access
        self.stand = stand

    # -- site variables --------------------

    @property
    def year(self) -> float:
        return self.stand.year

    @property
    def Y(self) -> float:
        return self.stand.geo_location[0]

    @property
    def X(self) -> float:
        return self.stand.geo_location[1]

    @property
    def Z(self) -> float:
        return self.stand.geo_location[2]

    @property
    def dd(self) -> float:
        return self.stand.degree_days

    @property
    def sea(self) -> float:
        return self.stand.sea_effect

    @property
    def lake(self) -> float:
        return self.stand.lake_effect

    @property
    def mal(self) -> LandUseCategoryVMI:
        return LandUseCategoryVMI(self.stand.land_use_category)

    @property
    def mty(self) -> SiteTypeVMI:
        return SiteTypeVMI(self.stand.site_type_category)

    @property
    def alr(self) -> SoilCategoryVMI:
        return SoilCategoryVMI(self.stand.soil_peatland_category)

    @property
    def verl(self) -> TaxClass:
        return TaxClass(self.stand.tax_class)

    @property
    def verlt(self) -> TaxClassReduction:
        return TaxClassReduction(self.stand.tax_class_reduction)

    # -- management vars (defaults) --------

    @property
    def spedom(self) -> Species:
        return domain_gm.spe2metsi(self.stand.reference_trees[0].species)

    @property
    def prt(self) -> Origin:
        return Origin.NATURAL

    # -- tree variables --------------------

    @cached_property
    def trees_f(self) -> list[float]:
        return [t.stems_per_ha for t in self.stand.reference_trees]

    @cached_property
    def trees_d(self) -> list[float]:
        return [(t.breast_height_diameter or 0.01) for t in self.stand.reference_trees]

    @cached_property
    def trees_h(self) -> list[float]:
        return [t.height for t in self.stand.reference_trees]

    '''
    @cached_property
    def trees_spe(self) -> list[Species]:
        return [spe2metsi(t.species) for t in self.stand.reference_trees]
    '''
    @cached_property
    def trees_spe(self) -> list[Species]:
        converted = []
        for t in self.stand.reference_trees:
            try:
                sp = domain_gm.spe2metsi(t.species)
                converted.append(sp)
            except Exception as e:
                print(f"[SpeciesError] Invalid tree species: {t.species} → {e}")
                raise
        return converted

    @cached_property
    def trees_t0(self) -> list[float]:
        return [self.year - t.biological_age for t in self.stand.reference_trees]

    @cached_property
    def trees_t13(self) -> list[float]:
        return [self.year - (t.breast_height_age or 0.0) for t in self.stand.reference_trees]

    @cached_property
    def trees_storie(self) -> list[Storie]:
        # TODO: derive or import storie data
        return [Storie.NONE for _ in self.stand.reference_trees]

    @cached_property
    def trees_snt(self) -> list[Origin]:
        return [Origin(t.origin + 1) if t.origin is not None else Origin.NATURAL
                for t in self.stand.reference_trees]


