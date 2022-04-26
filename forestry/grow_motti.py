from functools import cached_property
from typing import List
from forestry.ForestDataModels import ForestStand
import pymotti


def spe2motti(spe: int) -> pymotti.Species:
    # 1-5 match, but alders are combined.
    # TODO: this is a quick&dirty hack, the proper way is to convert on data import.
    return pymotti.Species(spe if spe <= 6 else spe+1)


class Model(pymotti.Predict):

    def __init__(self, stand: ForestStand):
        self.stand = stand

    #-- site variables --------------------

    @property
    def year(self) -> float:
        return self.stand.year

    @cached_property
    def X(self) -> float:
        lat, _, _, cs = self.stand.geo_location
        if cs != "ERTS-TM35FIN":
            raise NotImplementedError("TODO")
        return lat

    @cached_property
    def Y(self) -> float:
        _, lon, _, cs = self.stand.geo_location
        if cs != "ERTS-TM35FIN":
            raise NotImplementedError("TODO")
        return lon

    @property
    def Z(self) -> float:
        return self.stand.geo_location[2]

    @property
    def dd(self) -> float:
        return self.stand.degree_days

    @property
    def mal(self) -> pymotti.LandUseCategoryVMI:
        # coding matches RSD
        # TODO: this should not have zeros, should be checked when loading and not here.
        if self.stand.owner_category == 0:
            return pymotti.LandUseCategoryVMI.FOREST
        return pymotti.LandUseCategoryVMI(self.stand.owner_category)

    @property
    def mty(self) -> pymotti.SiteTypeVMI:
        # coding matches RSD
        return pymotti.SiteTypeVMI(self.stand.site_type_category)

    @property
    def alr(self) -> pymotti.SoilCategoryVMI:
        # coding matches RSD
        return pymotti.SoilCategoryVMI(self.stand.soil_peatland_category)

    @property
    def verl(self) -> pymotti.TaxClass:
        # coding matches RSD
        return pymotti.TaxClass(self.stand.tax_class)

    @property
    def verlt(self) -> pymotti.TaxClassReduction:
        # coding matches RSD
        return pymotti.TaxClassReduction(self.stand.tax_class_reduction)

    #-- management variables --------------------

    @property
    def spedom(self) -> pymotti.Species:
        # TODO: we don't have this, should be set in regeneration.
        return pymotti.Species.PINE

    @property
    def prt(self) -> pymotti.Origin:
        # TODO: we don't have this, should be set in regeneration.
        return pymotti.Origin.NATURAL

    # TODO: missing operations, since we don't have those yet.

    #-- tree variables --------------------

    @cached_property
    def trees_f(self) -> List[float]:
        return [t.stems_per_ha for t in self.stand.reference_trees]

    @cached_property
    def trees_d(self) -> List[float]:
        return [t.breast_height_diameter for t in self.stand.reference_trees]

    @cached_property
    def trees_h(self) -> List[float]:
        return [t.height for t in self.stand.reference_trees]

    @cached_property
    def trees_spe(self) -> List[pymotti.Species]:
        return [spe2motti(t.species) for t in self.stand.reference_trees]

    @cached_property
    def trees_t0(self) -> List[float]:
        return [self.year-t.biological_age for t in self.stand.reference_trees]

    @cached_property
    def trees_t13(self) -> List[float]:
        return [self.year-t.breast_height_age for t in self.stand.reference_trees]

    @cached_property
    def trees_storie(self) -> List[pymotti.Storie]:
        # TODO: we don't have this. should be set in regeneration, data import or by promotion rules.
        return [pymotti.Storie.NONE for _ in self.stand.reference_trees]

    @cached_property
    def trees_snt(self) -> List[pymotti.Origin]:
        # coding matches, but offset by 1
        # TODO: default origin should go into data loading, not here.
        return [pymotti.Origin(t.origin+1) if t.origin is not None else pymotti.Origin.NATURAL
                for t in self.stand.reference_trees]

    #-- strata variables --------------------
    # TODO: we don't have these yet.


def grow_motti(stand: ForestStand, **operation_params) -> ForestStand:
    growth = Model(stand).evolve()
    for i,t in enumerate(stand.reference_trees):
        t.stems_per_ha += growth.trees_if[i]
        t.breast_height_diameter += growth.trees_id[i]
        t.height += growth.trees_ih[i]
    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand
