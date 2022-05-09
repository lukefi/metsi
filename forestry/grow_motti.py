from functools import cached_property
from typing import List, Tuple
from forestdatamodel import ForestStand
import pymotti


def spe2motti(spe: int) -> pymotti.Species:
    """Convert RSD species code to Motti.

    The coding almost matches directly, but we have combined black/gray alders
    while Motti distinguishes between them. The current implementation just
    converts all alders to gray alder, but a proper implementation should
    store the Motti-coded species in :class:`ReferenceTree`
    so that we don't lose information on trees created by Motti."""
    return pymotti.Species(spe if spe <= 6 else spe + 1)


def _precompute_weather(stand: ForestStand):
    if not hasattr(stand, "_weather"):
        lat, lon, h, cs = stand.geo_location
        if cs != "ERTS-TM35FIN":
            raise NotImplementedError("TODO")
        p = pymotti.Predict(Y=lat, X=lon, Z=h)
        setattr(stand, "_weather", {"sea": p.sea, "lake": p.lake})


class MottiGrowthPredictor(pymotti.Predict):

    def __init__(self, stand: ForestStand):
        self.stand = stand

    # -- site variables --------------------

    @property
    def year(self) -> float:
        return self.stand.year

    @cached_property
    def Y(self) -> float:
        lat, _, _, cs = self.stand.geo_location
        if cs != "ERTS-TM35FIN":
            raise NotImplementedError("TODO")
        return lat

    @cached_property
    def X(self) -> float:
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
    def sea(self) -> float:
        _precompute_weather(self.stand)
        return getattr(self.stand, "_weather")["sea"]

    @property
    def lake(self) -> float:
        _precompute_weather(self.stand)
        return getattr(self.stand, "_weather")["lake"]

    @property
    def mal(self) -> pymotti.LandUseCategoryVMI:
        """Land use category. Our coding (RSD) matches Motti."""
        # TODO: this should not have zeros, should be checked when loading and not here.
        if self.stand.owner_category == 0:
            return pymotti.LandUseCategoryVMI.FOREST
        return pymotti.LandUseCategoryVMI(self.stand.owner_category)

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
