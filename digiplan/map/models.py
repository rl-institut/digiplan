"""Digiplan models."""

from typing import Optional

from django.contrib.gis.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from .managers import LabelMVTManager, RegionMVTManager, StaticMVTManager

# REGIONS


class Region(models.Model):
    """Base class for all regions - works as connector to other models."""

    class LayerType(models.TextChoices):
        """Region layer types."""

        COUNTRY = "country", _("Country")
        STATE = "state", _("State")
        DISTRICT = "district", _("District")
        MUNICIPALITY = "municipality", _("Municipality")

    layer_type = models.CharField(max_length=12, choices=LayerType.choices, null=False)

    class Meta:  # noqa: D106
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")


class Municipality(models.Model):
    """Model for region level municipality."""

    geom = models.MultiPolygonField(srid=4326)
    name = models.CharField(max_length=50, unique=True)
    area = models.FloatField()

    region = models.OneToOneField("Region", on_delete=models.DO_NOTHING, null=True)

    objects = models.Manager()
    vector_tiles = RegionMVTManager(columns=["id", "name", "bbox"])
    label_tiles = LabelMVTManager(geo_col="geom_label", columns=["id", "name"])

    data_file = "bkg_vg250_muns_region"
    layer = "vg250_gem"
    mapping = {"id": "id", "geom": "MULTIPOLYGON", "name": "name", "area": "area_km2"}

    class Meta:  # noqa: D106
        verbose_name = _("Municipality")
        verbose_name_plural = _("Municipalities")

    def __str__(self) -> str:
        """Return string representation of model."""
        return self.name

    @classmethod
    def area_whole_region(cls) -> float:
        """
        Return summed area of all municipalities.

        Returns
        -------
        float
            total area of all municipalities
        """
        return cls.objects.all().aggregate(Sum("area"))["area__sum"]


class Population(models.Model):
    """Population model."""

    year = models.IntegerField()
    value = models.IntegerField()
    entry_type = models.CharField(max_length=13)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)

    class Meta:  # noqa: D106
        verbose_name = _("Population")
        verbose_name_plural = _("Population")

    @classmethod
    def quantity(cls, year: int, mun_id: Optional[int] = None) -> int:
        """
        Calculate population in 2022 (either for municipality or for whole region).

        Parameters
        ----------
        year: int
            Year to filter population for
        mun_id: Optional[int]
            If given, population for given municipality are calculated. If not, for whole region.

        Returns
        -------
        int
            Value of population
        """
        if mun_id is not None:
            return cls.objects.filter(year=year, municipality__id=mun_id).aggregate(sum=Sum("value"))["sum"]
        return cls.objects.filter(year=year).aggregate(sum=Sum("value"))["sum"]

    @classmethod
    def population_history(cls, mun_id: int) -> models.QuerySet:
        """
        Get chart for population per municipality in different years.

        Parameters
        ----------
        mun_id: int
            Related municipality

        Returns
        -------
        models.QuerySet
            containing list of year/value pairs
        """
        return cls.objects.filter(municipality__id=mun_id).values_list("year", "value")

    @classmethod
    def population_per_municipality(cls) -> dict[int, int]:
        """
        Calculate population per municipality.

        Returns
        -------
        dict[int, int]
            Population per municipality
        """
        return {row.municipality_id: row.value for row in cls.objects.filter(year=2022)}

    @classmethod
    def density(cls, year: int, mun_id: Optional[int] = None) -> float:
        """
        Calculate population denisty in given year per km² (either for municipality or for whole region).

        Parameters
        ----------
        year: int
            Year to filter population for
        mun_id: Optional[int]
            If given, population per km² for given municipality are calculated. If not, for whole region.

        Returns
        -------
        float
            Value of population density
        """
        population = cls.quantity(year, mun_id=mun_id)

        if mun_id is not None:
            density = population / Municipality.objects.get(pk=mun_id).area
        else:
            density = population / Municipality.area_whole_region()
        return density

    @classmethod
    def density_history(cls, mun_id: int) -> dict:
        """
        Get chart for population density for the given municipality in different years.

        Parameters
        ----------
        mun_id: int
            Related municipality

        Returns
        -------
        dict
            Chart data to use in JS
        """
        density_history = []
        population_history = cls.objects.filter(municipality_id=mun_id).values_list("year", "value")

        for year, value in population_history:
            density = value / Municipality.objects.get(pk=mun_id).area
            density_history.append((year, density))

        return density_history

    @classmethod
    def density_per_municipality(cls) -> dict[int, int]:
        """
        Calculate population per municipality.

        Returns
        -------
        dict[int, int]
            Population per municipality
        """
        density = cls.population_per_municipality()
        for mun_id in density:
            density[mun_id] = density[mun_id] / Municipality.objects.get(pk=mun_id).area
        return density


class WindTurbine(models.Model):
    """Model holding wind turbines."""

    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    name_park = models.CharField(max_length=255, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    hub_height = models.FloatField(null=True)
    zip_code = models.CharField(max_length=50, null=True)
    rotor_diameter = models.FloatField(null=True)
    mun_id = models.IntegerField(null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom",
        columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated", "mun_id"],
    )

    data_file = "bnetza_mastr_wind_agg_region"
    layer = "bnetza_mastr_wind"
    mapping = {
        "geom": "POINT",
        "name": "name",
        "name_park": "name_park",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "hub_height": "hub_height",
        "rotor_diameter": "rotor_diameter",
        "zip_code": "zip_code",
        "mun_id": "municipality_id",
    }

    class Meta:  # noqa: D106
        verbose_name = _("Wind turbine")
        verbose_name_plural = _("Wind turbines")

    def __str__(self) -> str:
        """Return string representation of model."""
        return self.name

    @classmethod
    def quantity(cls, municipality_id: Optional[int] = None) -> int:
        """
        Calculate number of windturbines (either for municipality or for whole region).

        Parameters
        ----------
        municipality_id: Optional[int]
            If given, number of windturbines for given municipality are calculated. If not, for whole region.

        Returns
        -------
        int
            Sum of windturbines
        """
        values = cls.quantity_per_municipality()
        windturbines = 0

        if municipality_id is not None:
            windturbines = values[municipality_id]
        else:
            for index in values:
                windturbines += values[index]
        return windturbines

    @classmethod
    def quantity_per_municipality(cls) -> dict[int, int]:
        """
        Calculate number of wind turbines per municipality.

        Returns
        -------
        dict[int, int]
            wind turbines per municipality
        """
        return cls.objects.values("mun_id").annotate(units=Sum("unit_count")).values_list("mun_id", "units")

    @classmethod
    def wind_turbines_history(cls, municipality_id: int) -> dict:  # noqa: ARG003
        """
        Get chart for wind turbines.

        Parameters
        ----------
        municipality_id: int
            Related municipality

        Returns
        -------
        dict
            Chart data to use in JS
        """
        return [(2023, 2), (2046, 3), (2050, 4)]

    @classmethod
    def quantity_per_square(cls, municipality_id: Optional[int] = None) -> float:
        """
        Calculate number of windturbines per km² (either for municipality or for whole region).

        Parameters
        ----------
        municipality_id: Optional[int]
            If given, number of windturbines per km² for given municipality are calculated. If not, for whole region.

        Returns
        -------
        float
            Sum of windturbines per km²
        """
        windturbines = cls.quantity(municipality_id)

        if municipality_id is not None:
            return windturbines / Municipality.objects.get(pk=municipality_id).area
        return windturbines / Municipality.area_whole_region()

    @classmethod
    def wind_turbines_per_area_history(cls, municipality_id: int) -> dict:  # noqa: ARG003
        """
        Get chart for wind turbines per km².

        Parameters
        ----------
        municipality_id: int
            Related municipality

        Returns
        -------
        dict
            Chart data to use in JS
        """
        return [(2023, 2), (2046, 3), (2050, 4)]

    @classmethod
    def quantity_per_mun_and_area(cls) -> dict[int, int]:
        """
        Calculate windturbines per km² per municipality.

        Returns
        -------
        dict[int, int]
            windturbines per km² per municipality
        """
        windtubines = cls.quantity_per_municipality()
        for index in windtubines:
            windtubines[index] = windtubines[index] / Municipality.objects.get(pk=index).area
        return windtubines


class PVroof(models.Model):
    """Model holding PV roof."""

    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    power_limitation = models.CharField(max_length=50, null=True)
    mun_id = models.IntegerField(null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom",
        columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated", "mun_id"],
    )

    data_file = "bnetza_mastr_pv_roof_agg_region"
    layer = "bnetza_mastr_pv_roof"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "power_limitation": "power_limitation",
        "mun_id": "municipality_id",
    }

    class Meta:  # noqa: D106
        verbose_name = _("Roof-mounted PV")
        verbose_name_plural = _("Roof-mounted PVs")

    def __str__(self) -> str:
        """Return string representation of model."""
        return self.name


class PVground(models.Model):
    """Model holding PV on ground."""

    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    power_limitation = models.CharField(max_length=50, null=True)
    mun_id = models.IntegerField(null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom",
        columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated", "mun_id"],
    )

    data_file = "bnetza_mastr_pv_ground_agg_region"
    layer = "bnetza_mastr_pv_ground"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "power_limitation": "power_limitation",
        "mun_id": "municipality_id",
    }

    class Meta:  # noqa: D106
        verbose_name = _("Outdoor PV")
        verbose_name_plural = _("Outdoor PVs")


class Hydro(models.Model):
    """Hydro model."""

    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    water_origin = models.CharField(max_length=255, null=True)
    mun_id = models.IntegerField(null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom",
        columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated", "mun_id"],
    )

    data_file = "bnetza_mastr_hydro_agg_region"
    layer = "bnetza_mastr_hydro"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "water_origin": "water_origin",
        "mun_id": "municipality_id",
    }

    class Meta:  # noqa: D106
        verbose_name = _("Hydro")
        verbose_name_plural = _("Hydro")


class Biomass(models.Model):
    """Biomass model."""

    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    fuel_type = models.CharField(max_length=50, null=True)
    mun_id = models.IntegerField(null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom",
        columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated", "mun_id"],
    )

    data_file = "bnetza_mastr_biomass_agg_region"
    layer = "bnetza_mastr_biomass"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "fuel_type": "fuel_type",
        "mun_id": "municipality_id",
    }

    class Meta:  # noqa: D106
        verbose_name = _("Biomass")
        verbose_name_plural = _("Biomass")


class Combustion(models.Model):
    """Combustion model."""

    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    name_block = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    mun_id = models.IntegerField(null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom",
        columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated", "mun_id"],
    )

    data_file = "bnetza_mastr_combustion_agg_region"
    layer = "bnetza_mastr_combustion"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "name_block": "block_name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "mun_id": "municipality_id",
    }

    class Meta:  # noqa: D106
        verbose_name = _("Combustion")
        verbose_name_plural = _("Combustion")


class GSGK(models.Model):
    """GSGK model."""

    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    feedin_type = models.CharField(max_length=50, null=True)
    mun_id = models.IntegerField(null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom",
        columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated", "mun_id"],
    )

    data_file = "bnetza_mastr_gsgk_agg_region"
    layer = "bnetza_mastr_gsgk"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "feedin_type": "feedin_type",
        "mun_id": "municipality_id",
    }

    class Meta:  # noqa: D106
        verbose_name = _("GSGK")
        verbose_name_plural = _("GSGK")


class Storage(models.Model):
    """Storage model."""

    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    mun_id = models.IntegerField(null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom",
        columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated", "mun_id"],
    )

    data_file = "bnetza_mastr_storage_agg_region"
    layer = "bnetza_mastr_storage"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "mun_id": "municipality_id",
    }

    class Meta:  # noqa: D106
        verbose_name = _("Storage")
        verbose_name_plural = _("Storages")


class StaticRegionModel(models.Model):
    """Base class for static region models."""

    geom = models.MultiPolygonField(srid=4326)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(columns=[])

    mapping = {"geom": "MULTIPOLYGON"}

    class Meta:  # noqa: D106
        abstract = True


class AirTraffic(StaticRegionModel):  # noqa: D101
    data_file = "air_traffic_control_system_region"
    layer = "air_traffic_control_system"


class Aviation(StaticRegionModel):  # noqa: D101
    data_file = "aviation_region"
    layer = "aviation"


class BiosphereReserve(StaticRegionModel):  # noqa: D101
    data_file = "biosphere_reserve_region"
    layer = "biosphere_reserve"


class DrinkingWaterArea(StaticRegionModel):  # noqa: D101
    data_file = "drinking_water_protection_area_region"
    layer = "drinking_water_protection_area"


class FaunaFloraHabitat(StaticRegionModel):  # noqa: D101
    data_file = "fauna_flora_habitat_region"
    layer = "fauna_flora_habitat"


class Floodplain(StaticRegionModel):  # noqa: D101
    data_file = "floodplain_region"
    layer = "floodplain"


class Forest(StaticRegionModel):  # noqa: D101
    data_file = "forest_region"
    layer = "forest"


class Grid(StaticRegionModel):  # noqa: D101
    data_file = "grid_region"
    layer = "grid"


class Industry(StaticRegionModel):  # noqa: D101
    data_file = "industry_region"
    layer = "industry"


class LandscapeProtectionArea(StaticRegionModel):  # noqa: D101
    data_file = "landscape_protection_area_region"
    layer = "landscape_protection_area"


class LessFavouredAreasAgricultural(StaticRegionModel):  # noqa: D101
    data_file = "less_favoured_areas_agricultural_region"
    layer = "less_favoured_areas_agricultural"


class Military(StaticRegionModel):  # noqa: D101
    data_file = "military_region"
    layer = "military"


class NatureConservationArea(StaticRegionModel):  # noqa: D101
    data_file = "nature_conservation_area_region"
    layer = "nature_conservation_area"


class Railway(StaticRegionModel):  # noqa: D101
    data_file = "railway_region"
    layer = "railway"


class RoadRailway500m(StaticRegionModel):  # noqa: D101
    data_file = "road_railway-500m_region"
    layer = "road_railway-500m"


class Road(StaticRegionModel):  # noqa: D101
    data_file = "road_region"
    layer = "road"


class Settlement0m(StaticRegionModel):  # noqa: D101
    data_file = "settlement-0m_region"
    layer = "settlement-0m"


class SoilQualityHigh(StaticRegionModel):  # noqa: D101
    data_file = "soil_quality_high_region"
    layer = "soil_quality_high"


class SoilQualityLow(StaticRegionModel):  # noqa: D101
    data_file = "soil_quality_low_region"
    layer = "soil_quality_low"


class SpecialProtectionArea(StaticRegionModel):  # noqa: D101
    data_file = "special_protection_area_region"
    layer = "special_protection_area"


class Water(StaticRegionModel):  # noqa: D101
    data_file = "water_region"
    layer = "water"


class PotentialareaPVAgricultureLFAOff(StaticRegionModel):  # noqa: D101
    data_file = "potentialarea_pv_agriculture_lfa-off_region"
    layer = "potentialarea_pv_agriculture_lfa-off_region"


class PotentialareaPVRoadRailway(StaticRegionModel):  # noqa: D101
    data_file = "potentialarea_pv_road_railway_region"
    layer = "potentialarea_pv_road_railway_region"


class PotentialareaWindSTP2018Vreg(StaticRegionModel):  # noqa: D101
    data_file = "potentialarea_wind_stp_2018_vreg"
    layer = "potentialarea_wind_stp_2018_vreg"


class PotentialareaWindSTP2027Repowering(StaticRegionModel):  # noqa: D101
    data_file = "potentialarea_wind_stp_2027_repowering"
    layer = "potentialarea_wind_stp_2027_repowering"


class PotentialareaWindSTP2027SearchAreaForestArea(StaticRegionModel):  # noqa: D101
    data_file = "potentialarea_wind_stp_2027_search_area_forest_area"
    layer = "potentialarea_wind_stp_2027_search_area_forest_area"


class PotentialareaWindSTP2027SearchAreaOpenArea(StaticRegionModel):  # noqa: D101
    data_file = "potentialarea_wind_stp_2027_search_area_open_area"
    layer = "potentialarea_wind_stp_2027_search_area_open_area"


class PotentialareaWindSTP2027VR(StaticRegionModel):  # noqa: D101
    data_file = "potentialarea_wind_stp_2027_vr"
    layer = "potentialarea_wind_stp_2027_vr"


RENEWABLES = (WindTurbine, PVroof, PVground, Hydro, Biomass)
