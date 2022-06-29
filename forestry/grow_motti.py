from functools import cached_property
from typing import List, Tuple
from forestdatamodel.enums.internal import TreeSpecies
from forestdatamodel.model import ForestStand
from forestdatamodel.conversion import internal2mela
import pymotti


def spe2motti(spe: int) -> pymotti.Species:
    """Convert RSD species code to Motti.

    The coding almost matches directly, but we have combined black/gray alders
    while Motti distinguishes between them. The current implementation just
    converts all alders to gray alder, but a proper implementation should
    store the Motti-coded species in :class:`ReferenceTree`
    so that we don't lose information on trees created by Motti."""
    spe = internal2mela.species_map[TreeSpecies(spe)].value
    return pymotti.Species(spe if spe <= 6 else spe + 1)


class MottiGrowthPredictor(pymotti.Predict):

    def __init__(self, stand: ForestStand):
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
        return -1 if self.stand.geo_location[2] is None else self.stand.geo_location[2]

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
    def mal(self) -> pymotti.LandUseCategoryVMI:
        """Land use category. Our coding (RSD) matches Motti."""
        return pymotti.LandUseCategoryVMI(self.stand.land_use_category)

    @property
    def mty(self) -> pymotti.SiteTypeVMI:
        """Site type category. Our coding (RSD) matches Motti."""
        return pymotti.SiteTypeVMI(self.stand.site_type_category)

    @property
    def alr(self) -> pymotti.SoilCategoryVMI:
        """Soil category. Our coding (RSD) matches Motti."""
        return pymotti.SoilCategoryVMI(self.stand.soil_peatland_category)

    @property
    def verl(self) -> pymotti.TaxClass:
        """Tax class. Our coding (RSD) matches Motti."""
        return pymotti.TaxClass(self.stand.tax_class)

    @property
    def verlt(self) -> pymotti.TaxClassReduction:
        """Tax class reduction. Our coding (RSD) matches Motti."""
        return pymotti.TaxClassReduction(self.stand.tax_class_reduction)

    # -- management variables --------------------

    @property
    def spedom(self) -> pymotti.Species:
        """Main species.

        We don't have this yet, should be set in regeneration."""
        return pymotti.Species.PINE

    @property
    def prt(self) -> pymotti.Origin:
        """Regeneration method.

        We don't have this yet, should be set in regeneration."""
        return pymotti.Origin.NATURAL

    # TODO: missing operations, since we don't have those yet.

    # -- tree variables --------------------

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
        return [self.year - t.biological_age for t in self.stand.reference_trees]

    @cached_property
    def trees_t13(self) -> List[float]:
        return [self.year - t.breast_height_age for t in self.stand.reference_trees]

    @cached_property
    def trees_storie(self) -> List[pymotti.Storie]:
        """Storie of trees.

        We don't have this yet, should be set in regeneration.
        For imported trees, should either come from data, be computed or just set to NONE."""
        return [pymotti.Storie.NONE for _ in self.stand.reference_trees]

    @cached_property
    def trees_snt(self) -> List[pymotti.Origin]:
        """Origin of trees. Our coding (RSD) matches, but is offset by 1."""
        # TODO: default origin should go into data loading, not here.
        return [pymotti.Origin(t.origin + 1) if t.origin is not None else pymotti.Origin.NATURAL
                for t in self.stand.reference_trees]

    # -- strata variables --------------------
    # TODO: we don't have these yet.


def grow_motti(input: Tuple[ForestStand, None], **operation_parameters) -> Tuple[ForestStand, None]:
    stand, _ = input
    growth = MottiGrowthPredictor(stand).evolve()
    for i, t in enumerate(stand.reference_trees):
        t.stems_per_ha += growth.trees_if[i]
        t.breast_height_diameter += growth.trees_id[i]
        t.height += growth.trees_ih[i]
    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, None
