from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from .managers import RegionMVTManager, LabelMVTManager, MVTManager


class Region(models.Model):
    """Base class for all regions - works as connector to other models"""

    class LayerType(models.TextChoices):
        COUNTRY = "country", _("Land")
        STATE = "state", _("Bundesland")
        DISTRICT = "district", _("Kreis")
        MUNICIPALITY = "municipality", _("Gemeinde")

    layer_type = models.CharField(max_length=12, choices=LayerType.choices, null=False)


# REGIONS


class District(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    name = models.CharField(max_length=50)
    area = models.FloatField()
    population = models.BigIntegerField()
    hospitals = models.IntegerField()
    den_p_h_km = models.FloatField(null=True)

    objects = models.Manager()
    vector_tiles = RegionMVTManager(columns=["id", "name", "bbox"])
    label_tiles = LabelMVTManager(geo_col="geom_label", columns=["id", "name"])

    data_file = "AdminAreas"
    mapping = {
        "geom": "MULTIPOLYGON",
        "name": "DISTRICT",
        "area": "Shape__Are",
        "population": "pop_2020",
        "hospitals": "NUM_hosp",
        "den_p_h_km": "den_p_h_km",
    }

    def __str__(self):
        return self.name


# LAYER


class Grid(models.Model):
    geom = models.MultiLineStringField(srid=4326)
    source = models.CharField(max_length=100)

    objects = models.Manager()
    vector_tiles = MVTManager(columns=["id", "source"])

    data_file = "Electricity_Infrastructure"
    layer = "GridNetwork"
    mapping = {
        "geom": "MULTILINESTRING",
        "source": "source",
    }

    def __str__(self):
        return self.source


class Nightlight(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    dn = models.IntegerField()

    objects = models.Manager()
    vector_tiles = RegionMVTManager(columns=["id", "dn"])

    data_file = "Electricity_Infrastructure"
    layer = "NightLights_Binary"
    mapping = {
        "geom": "MULTIPOLYGON",
        "dn": "DN",
    }


class HC_Facilities(models.Model):
    geom = models.PointField(srid=4326)
    nightlight_distance = models.IntegerField(null=True)

    filters = ["nightlight_distance"]

    objects = models.Manager()
    vector_tiles = RegionMVTManager(columns=["id", "nightlight_distance"])

    data_file = "HealthCare_Insfrastructure"
    layer = "HC_Facilities"
    mapping = {
        "geom": "POINT",
        "nightlight_distance": "nlj_DN",
    }
