"""Digiplan models."""


import pandas as pd
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
    def quantity_per_municipality_per_year(cls) -> pd.DataFrame:
        """
        Return population in 2022 per municipality and year.

        Returns
        -------
        pd.DataFrame
            Population per municipality (index) and year (column)
        """
        population_per_year = (
            pd.DataFrame.from_records(cls.objects.all().values("municipality__id", "year", "value"))  # noqa: PD010
            .set_index("municipality__id")
            .pivot(columns="year")
        )
        population_per_year.columns = population_per_year.columns.droplevel(0)
        return population_per_year


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
    def quantity_per_municipality(cls) -> pd.DataFrame:
        """
        Calculate number of wind turbines per municipality.

        Returns
        -------
        dpd.DataFrame
            wind turbines per municipality
        """
        queryset = cls.objects.values("mun_id").annotate(units=Sum("unit_count")).values("mun_id", "units")
        wind_turbines = pd.DataFrame.from_records(queryset).set_index("mun_id")
        return wind_turbines["units"].reindex(Municipality.objects.all().values_list("id", flat=True), fill_value=0)


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
