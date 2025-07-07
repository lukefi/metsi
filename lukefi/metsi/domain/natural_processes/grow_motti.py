# pylint: disable=invalid-name

from functools import cached_property
import pymotti  # type: ignore # pylint: disable=import-error
from lukefi.metsi.data.conversion import internal2mela
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.domain.natural_processes.util import update_stand_growth


def spe2motti(spe: int) -> pymotti.Species:
    """Convert RST species code to Motti.

    The coding almost matches directly, but we have combined black/gray alders
    while Motti distinguishes between them. The current implementation just
    converts all alders to gray alder, but a proper implementation should
    store the Motti-coded species in :class:`ReferenceTree`
    so that we don't lose information on trees created by Motti."""
    spe = internal2mela.species_map[TreeSpecies(spe)].value
    return pymotti.Species(spe if spe <= 6 else spe + 1)


class MottiGrowthPredictor(pymotti.Predict):
    """
    Extend pymotti.Predict to provide properties from forest-data-model based ForestStand and ReferenceTree objects
    """

    def __init__(self, stand: ForestStand):
        self.stand = stand

    # -- site variables --------------------

    @property
    def year(self) -> float:
        """Calendar year which the stand data represents"""
        return self.stand.year

    @property
    def Y(self) -> float:
        """latitude assumed to be EPSG:2393 CRS value divided by 1000"""
        return self.stand.geo_location[0]

    @property
    def X(self) -> float:
        """longitude assumed to be EPSG:2393 CRS value divided by 1000"""
        return self.stand.geo_location[1]

    @property
    def Z(self) -> float:
        """Stand altitude above sea level (m)"""
        return self.stand.geo_location[2]

    @property
    def dd(self) -> float:
        """Temperature (C) sum of the stand """
        return self.stand.degree_days

    @property
    def sea(self) -> float:
        """Sea effect value of the stand"""
        return self.stand.sea_effect

    @property
    def lake(self) -> float:
        """Lake effect value of the stand"""
        return self.stand.lake_effect

    @property
    def mal(self) -> pymotti.LandUseCategoryVMI:
        """Land use category. Our coding (RST) matches Motti."""
        return pymotti.LandUseCategoryVMI(self.stand.land_use_category)

    @property
    def mty(self) -> pymotti.SiteTypeVMI:
        """Site type category. Our coding (RST) matches Motti."""
        return pymotti.SiteTypeVMI(self.stand.site_type_category)

    @property
    def alr(self) -> pymotti.SoilCategoryVMI:
        """Soil category. Our coding (RST) matches Motti."""
        return pymotti.SoilCategoryVMI(self.stand.soil_peatland_category)

    @property
    def verl(self) -> pymotti.TaxClass:
        """Tax class. Our coding (RST) matches Motti."""
        return pymotti.TaxClass(self.stand.tax_class)

    @property
    def verlt(self) -> pymotti.TaxClassReduction:
        """Tax class reduction. Our coding (RST) matches Motti."""
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
    def trees_f(self) -> list[float]:
        """Tree stem count per hectare"""
        return [t.stems_per_ha for t in self.stand.reference_trees]

    @cached_property
    def trees_d(self) -> list[float]:
        """Breast height diameter (cm). Force at least 0.01, pymotti just crashes with 0 basal area otherwise."""
        return [(t.breast_height_diameter or 0.01) for t in self.stand.reference_trees]

    @cached_property
    def trees_h(self) -> list[float]:
        """Height (m)"""
        return [t.height for t in self.stand.reference_trees]

    @cached_property
    def trees_spe(self) -> list[pymotti.Species]:
        """species code converted to Motti compatible coding"""
        return [spe2motti(t.species) for t in self.stand.reference_trees]

    @cached_property
    def trees_t0(self) -> list[float]:
        """Year of birth computed from stand year and tree age"""
        return [self.year - t.biological_age for t in self.stand.reference_trees]

    @cached_property
    def trees_t13(self) -> list[float]:
        """Breast height achievement year computed from stand year and breast height age"""
        return [self.year - (t.breast_height_age or 0.0) for t in self.stand.reference_trees]

    @cached_property
    def trees_storie(self) -> list[pymotti.Storie]:
        """Storie of trees.

        We don't have this yet, should be set in regeneration.
        For imported trees, should either come from data, be computed or just set to NONE."""
        return [pymotti.Storie.NONE for _ in self.stand.reference_trees]

    @cached_property
    def trees_snt(self) -> list[pymotti.Origin]:
        """Origin of trees. Our coding (RST) matches, but is offset by 1."""
        # TODO: default origin should go into data loading, not here.
        return [pymotti.Origin(t.origin + 1) if t.origin is not None else pymotti.Origin.NATURAL
                for t in self.stand.reference_trees]

    # -- strata variables --------------------
    # TODO: we don't have these yet.


def grow_motti(input_: tuple[ForestStand, None], **operation_parameters) -> tuple[ForestStand, None]:
    step = operation_parameters.get('step', 5)
    stand, _ = input_
    growth = MottiGrowthPredictor(stand).evolve()
    # Motti returns deltas.
    diameters = list(map(lambda x: x[0].breast_height_diameter + x[1], zip(stand.reference_trees, growth.trees_id)))
    heights = list(map(lambda x: x[0].height + x[1], zip(stand.reference_trees, growth.trees_ih)))
    stems = list(map(lambda x: x[0].stems_per_ha + x[1], zip(stand.reference_trees, growth.trees_if)))
    update_stand_growth(stand, diameters, heights, stems, step)
    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, None
