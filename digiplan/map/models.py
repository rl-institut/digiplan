import json
import os
from dataclasses import dataclass
from enum import Enum

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from config.settings.base import DATA_DIR

from .managers import LabelMVTManager, RegionMVTManager, StaticMVTManager


class LayerFilterType(Enum):
    Range = 0
    Dropdown = 1


@dataclass
class LayerFilter:
    name: str
    type: LayerFilterType = LayerFilterType.Range  # noqa: A003


class ModelMappingMixin:
    def get_captions(self, list_of_attributes):
        filename = "bnetza_mastr_attribute_captions.json"

        mapping_dict = {
            "WindTurbine": "bnetza_mastr_wind_region",
            "PVroof": "bnetza_mastr_pv_roof_region",
            "PVground": "bnetza_mastr_pv_ground_region",
            "Hydro": "bnetza_mastr_hydro_region",
            "Biomass": "bnetza_mastr_biomass_region",
            "Combustion": "bnetza_mastr_combustion_region",
        }

        checked_classname = mapping_dict[str(self.__class__.__name__)]
        with open(os.path.join(DATA_DIR, filename), encoding="utf8") as file:
            jsonfile = json.load(file)
            caption_dict_name = jsonfile["datasets_caption_map"][checked_classname]

            for attribute in list_of_attributes:
                caption = jsonfile["captions"][caption_dict_name][attribute]
                list_of_attributes[list_of_attributes.index(attribute)] = caption

            return list_of_attributes


# REGIONS


class Region(models.Model):
    """Base class for all regions - works as connector to other models"""

    class LayerType(models.TextChoices):
        COUNTRY = "country", _("Land")
        STATE = "state", _("Bundesland")
        DISTRICT = "district", _("Kreis")
        MUNICIPALITY = "municipality", _("Gemeinde")

    layer_type = models.CharField(max_length=12, choices=LayerType.choices, null=False)


class Municipality(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    name = models.CharField(max_length=50, unique=True)

    region = models.OneToOneField("Region", on_delete=models.DO_NOTHING, null=True)

    objects = models.Manager()
    vector_tiles = RegionMVTManager(columns=["id", "name", "bbox"])
    label_tiles = LabelMVTManager(geo_col="geom_label", columns=["id", "name"])

    data_file = "municipality"
    layer = "municipality"
    mapping = {
        "geom": "MULTIPOLYGON",
        "name": "name",
    }

    def __str__(self):
        return self.name


class WindTurbine(models.Model):
    geom = models.PointField(srid=4326)  # maybe MultiPointField
    name = models.CharField(max_length=255, null=True)
    name_park = models.CharField(max_length=255, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    hub_height = models.FloatField(null=True)
    zip_code = models.CharField(max_length=50, null=True)
    rotor_diameter = models.FloatField(null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom", columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated"]
    )

    data_file = "bnetza_mastr_wind_agg_abw"
    layer = "bnetza_mastr_wind_abw"
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
    }

    def __str__(self):
        return self.name


class PVroof(models.Model):
    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    power_limitation = models.CharField(max_length=50, null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom", columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated"]
    )

    data_file = "bnetza_mastr_pv_roof_agg_abw"
    layer = "bnetza_mastr_pv_roof_abw"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "power_limitation": "power_limitation",
    }

    def __str__(self):
        return self.name


class PVground(models.Model):
    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    power_limitation = models.CharField(max_length=50, null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom", columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated"]
    )

    data_file = "bnetza_mastr_pv_ground_agg_abw"
    layer = "bnetza_mastr_pv_ground_abw"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "power_limitation": "power_limitation",
    }


class Hydro(models.Model):
    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    water_origin = models.CharField(max_length=255, null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom", columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated"]
    )

    data_file = "bnetza_mastr_hydro_agg_abw"
    layer = "bnetza_mastr_hydro_abw"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "water_origin": "water_origin",
    }


class Biomass(models.Model):
    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)
    fuel_type = models.CharField(max_length=50, null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom", columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated"]
    )

    data_file = "bnetza_mastr_biomass_agg_abw"
    layer = "bnetza_mastr_biomass_abw"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
        "fuel_type": "fuel_type",
    }


class Combustion(models.Model):
    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=255, null=True)
    name_block = models.CharField(max_length=255, null=True)
    zip_code = models.CharField(max_length=50, null=True)
    geometry_approximated = models.BooleanField()
    unit_count = models.BigIntegerField(null=True)
    capacity_net = models.FloatField(null=True)

    objects = models.Manager()
    vector_tiles = StaticMVTManager(
        geo_col="geom", columns=["id", "name", "unit_count", "capacity_net", "geometry_approximated"]
    )

    data_file = "bnetza_mastr_combustion_agg_abw"
    layer = "bnetza_mastr_combustion_abw"

    mapping = {
        "geom": "POINT",
        "name": "name",
        "name_block": "block_name",
        "zip_code": "zip_code",
        "geometry_approximated": "geometry_approximated",
        "unit_count": "unit_count",
        "capacity_net": "capacity_net",
    }
