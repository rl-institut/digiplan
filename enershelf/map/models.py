from dataclasses import dataclass
from enum import Enum

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .managers import RegionMVTManager, LabelMVTManager, MVTManager, ClusterMVTManager


class LayerFilterType(Enum):
    Range = 0
    Dropdown = 1


@dataclass
class LayerFilter:
    name: str
    type: LayerFilterType = LayerFilterType.Range


# REGIONS


class Region(models.Model):
    """Base class for all regions - works as connector to other models"""

    class LayerType(models.TextChoices):
        COUNTRY = "country", _("Land")
        STATE = "state", _("Bundesland")
        DISTRICT = "district", _("Kreis")
        MUNICIPALITY = "municipality", _("Gemeinde")

    layer_type = models.CharField(max_length=12, choices=LayerType.choices, null=False)


class Country(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    name = models.CharField(max_length=50, unique=True)
    area = models.FloatField()
    population = models.BigIntegerField()

    region = models.OneToOneField("Region", on_delete=models.DO_NOTHING, null=True)

    objects = models.Manager()
    vector_tiles = RegionMVTManager(columns=["id", "name", "bbox"])
    label_tiles = LabelMVTManager(geo_col="geom_label", columns=["id", "name"])

    data_file = "Gha_AdminBoundaries"
    layer = "Gha_NationalBoundary_00"
    mapping = {
        "geom": "MULTIPOLYGON",
        "name": "Country",
        "area": "AreaKm2",
        "population": "Pop2020",
    }

    def __str__(self):
        return self.name


class State(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    name = models.CharField(max_length=50, unique=True)
    area = models.FloatField()
    population = models.BigIntegerField()

    region = models.OneToOneField("Region", on_delete=models.DO_NOTHING, null=True)

    objects = models.Manager()
    vector_tiles = RegionMVTManager(columns=["id", "name", "bbox"])
    label_tiles = LabelMVTManager(geo_col="geom_label", columns=["id", "name"])

    data_file = "Gha_AdminBoundaries"
    layer = "Gha_Regions_01"
    mapping = {
        "geom": "MULTIPOLYGON",
        "name": "Region",
        "area": "Area_km2",
        "population": "Pop2020",
    }

    def __str__(self):
        return self.name


class District(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    name = models.CharField(max_length=50, unique=True)
    area = models.FloatField()
    population = models.BigIntegerField()

    region = models.OneToOneField("Region", on_delete=models.DO_NOTHING, null=True)
    state = models.ForeignKey("State", on_delete=models.CASCADE, related_name="districts")

    objects = models.Manager()
    vector_tiles = RegionMVTManager(columns=["id", "name", "bbox"])
    label_tiles = LabelMVTManager(geo_col="geom_label", columns=["id", "name"])

    data_file = "Gha_AdminBoundaries"
    layer = "Gha_Districts_02"
    mapping = {
        "geom": "MULTIPOLYGON",
        "name": "District",
        "area": "Area_km2",
        "population": "Pop2020",
        "state": {"name": "Region"},  # ForeignKey see https://stackoverflow.com/a/46689928/5804947
    }

    def __str__(self):
        return self.name


# LAYER


class ClusterModel(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    area = models.FloatField()
    population = models.IntegerField()
    number_of_hospitals = models.IntegerField()

    objects = models.Manager()
    vector_tiles = ClusterMVTManager(columns=["id", "area", "population", "number_of_hospitals", "lat", "lon"])

    filters = [
        LayerFilter("area"),
        LayerFilter("number_of_hospitals"),
        LayerFilter("population"),
    ]

    data_file = "Population_Clusters"
    mapping = {
        "geom": "MULTIPOLYGON",
        "area": "Area_km2",
        "population": "Pop2020",
        "number_of_hospitals": "Num_hosp",
        "district": {"name": "District"},  # ForeignKey see https://stackoverflow.com/a/46689928/5804947
    }

    class Meta:
        abstract = True

    def __str__(self):
        return self.district.name


class BuiltUpAreas(ClusterModel):
    distance_to_grid = models.FloatField()
    distance_to_light = models.FloatField()

    district = models.ForeignKey("District", on_delete=models.CASCADE, related_name="built_up_areas")

    vector_tiles = ClusterMVTManager(
        columns=[
            "id",
            "area",
            "population",
            "number_of_hospitals",
            "distance_to_grid",
            "distance_to_light",
            "lat",
            "lon",
            "state_name",
            "district_name",
        ]
    )

    layer = "Gha_Built_Up_Areas"
    mapping = {
        "geom": "MULTIPOLYGON",
        "area": "Area_km2",
        "population": "Pop2020",
        "number_of_hospitals": "Num_hosp",
        "distance_to_grid": "Dist2Grid_mtr",
        "distance_to_light": "Dist2Light_mtr",
        "district": {"name": "District"},  # ForeignKey see https://stackoverflow.com/a/46689928/5804947
    }


class Settlements(ClusterModel):
    distance_to_grid = models.FloatField()
    distance_to_light = models.FloatField()

    district = models.ForeignKey("District", on_delete=models.CASCADE, related_name="settlements")

    vector_tiles = ClusterMVTManager(
        columns=[
            "id",
            "area",
            "population",
            "number_of_hospitals",
            "distance_to_grid",
            "distance_to_light",
            "lat",
            "lon",
            "state_name",
            "district_name",
        ]
    )

    layer = "Gha_Small_Settlement_Areas"
    mapping = {
        "geom": "MULTIPOLYGON",
        "area": "Area_km2",
        "population": "Pop2020",
        "number_of_hospitals": "Num_hosp",
        "distance_to_grid": "Dist2Grid_mtr",
        "distance_to_light": "Dist2Light_mtr",
        "district": {"name": "District"},  # ForeignKey see https://stackoverflow.com/a/46689928/5804947
    }


class Hamlets(ClusterModel):
    district = models.ForeignKey("District", on_delete=models.CASCADE, related_name="hamlets")

    layer = "Gha_Hamlets"
    mapping = {
        "geom": "MULTIPOLYGON",
        "area": "Area_km2",
        "population": "Pop2020",
        "number_of_hospitals": "Num_Hosp",
        "district": {"name": "District"},  # ForeignKey see https://stackoverflow.com/a/46689928/5804947
    }

    filters = []


# class Grid(models.Model):
#     geom = models.MultiLineStringField(srid=4326)
#     source = models.CharField(max_length=100)
#
#     objects = models.Manager()
#     vector_tiles = MVTManager(columns=["id", "source"])
#
#     data_file = "Electricity_Infrastructure"
#     layer = "GridNetwork"
#     mapping = {
#         "geom": "MULTILINESTRING",
#         "source": "source",
#     }
#
#     def __str__(self):
#         return self.source


class Nightlight(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    distance = models.IntegerField()

    objects = models.Manager()
    vector_tiles = MVTManager(columns=["id", "distance"])

    data_file = "Energy_Infrastructure"
    layer = "Gha_Nightlights_Binary"
    mapping = {
        "geom": "MULTIPOLYGON",
        "distance": "DN",
    }


class Hospitals(models.Model):
    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=254)
    type = models.CharField(max_length=254)
    town = models.CharField(max_length=254, null=True)
    ownership = models.CharField(max_length=254)

    district = models.ForeignKey("District", on_delete=models.CASCADE, related_name="hospitals")

    objects = models.Manager()
    vector_tiles = MVTManager(columns=["id", "name", "type", "town", "ownership"])

    data_file = "HealthCare_Infrastructure"
    layer = "Gha_HealthCareFacilties_total"
    mapping = {
        "id": "FID",
        "geom": "POINT",
        "name": "facility_name",
        "type": "Type",
        "town": "Town",
        "ownership": "Ownership",
        "district": {"name": "District"},
    }


class HospitalsSimulated(models.Model):
    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=254)
    type = models.CharField(max_length=254)
    town = models.CharField(max_length=254, null=True)
    ownership = models.CharField(max_length=254)
    settlement_area = models.FloatField()
    settlement_population = models.IntegerField()
    settlement_type = models.CharField(max_length=254)
    lcoe = models.FloatField()
    electricity_demand = models.FloatField()
    cap_ex = models.FloatField()
    pv_capacity = models.FloatField()

    district = models.ForeignKey("District", on_delete=models.CASCADE, related_name="simulated_hospitals")

    objects = models.Manager()
    vector_tiles = MVTManager(columns=["id", "name", "type", "town", "ownership", "settlement_type", "lcoe"])

    filters = [LayerFilter("settlement_type", type=LayerFilterType.Dropdown)]

    data_file = "HealthCare_Infrastructure"
    layer = "Gha_185_Selected_HFCs"
    mapping = {
        "geom": "POINT",
        "name": "facility_name",
        "type": "Type",
        "town": "Town",
        "ownership": "Ownership",
        "settlement_area": "Settlement_area",
        "settlement_population": "Settlement_pop2020",
        "settlement_type": "Settlement_type",
        "lcoe": "LCOE_soft",
        "electricity_demand": "Elct_demand",
        "cap_ex": "CapEx_soft",
        "pv_capacity": "PV_capacity",
        "district": {"name": "District"},
    }
