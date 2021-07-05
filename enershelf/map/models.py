from django.contrib.gis.db import models
from .managers import RegionMVTManager, LabelMVTManager, MVTManager, CenterMVTManager


# REGIONS


class Region(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    name = models.CharField(max_length=50, unique=True)

    objects = models.Manager()
    vector_tiles = RegionMVTManager(columns=["id", "name", "bbox"])
    label_tiles = LabelMVTManager(geo_col="geom_label", columns=["id", "name"])

    data_file = "Gha_AdminBoundaries"
    layer = "Gha_Regions_01"
    mapping = {
        "geom": "MULTIPOLYGON",
        "name": "Region",
    }

    def __str__(self):
        return self.name


class District(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    name = models.CharField(max_length=50, unique=True)
    area = models.FloatField()
    population = models.BigIntegerField()

    region = models.ForeignKey("Region", on_delete=models.CASCADE, related_name="districts")

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
        "region": {"name": "Region"},  # ForeignKey see https://stackoverflow.com/a/46689928/5804947
    }

    def __str__(self):
        return self.name


# LAYER


class Cluster(models.Model):
    geom = models.MultiPolygonField(srid=4326)
    area = models.FloatField()
    population_density = models.FloatField()

    district = models.ForeignKey("District", on_delete=models.CASCADE, related_name="cluster")
    closest_hospital = models.ForeignKey("Hospitals", on_delete=models.CASCADE, related_name="cluster", null=True)

    objects = models.Manager()
    vector_tiles = CenterMVTManager(columns=["id", "area", "population_density", "lat", "lon"])

    filters = ["area", "population_density"]

    data_file = "Population_Clusters"
    layer = "Gha_PopClusters_attributed"
    mapping = {
        "geom": "MULTIPOLYGON",
        "area": "cluster_areakm2",
        "population_density": "cluster_PopDen",
        "district": {"name": "District"},  # ForeignKey see https://stackoverflow.com/a/46689928/5804947
        "closest_hospital": {"id": "id_closestFacility"},
    }

    def __str__(self):
        return self.district.name


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
    layer = "Ghana_Nightlights_Binary"
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
    population_per_hospital = models.FloatField()
    catchment_area_hospital = models.FloatField()
    nightlight = models.IntegerField(null=True)

    district = models.ForeignKey("District", on_delete=models.CASCADE, related_name="hospitals")

    objects = models.Manager()
    vector_tiles = MVTManager(
        columns=["id", "name", "type", "town", "ownership", "population_per_hospital", "catchment_area_hospital"]
    )

    filters = ["population_per_hospital", "catchment_area_hospital"]

    data_file = "HealthCare_Infrastructure"
    layer = "Gha_HealthCareFacilities_total"
    mapping = {
        "id": "FID",
        "geom": "POINT",
        "name": "facility_name",
        "type": "Type",
        "town": "Town",
        "ownership": "Ownership",
        "population_per_hospital": "Pop_per_hosp",
        "catchment_area_hospital": "Catchment_area_hosp",
        "nightlight": "Nightlight_DigitalNumber",
        "district": {"name": "District"},
    }


class HospitalsSimulated(models.Model):
    geom = models.PointField(srid=4326)
    name = models.CharField(max_length=254)
    type = models.CharField(max_length=254)
    town = models.CharField(max_length=254, null=True)
    ownership = models.CharField(max_length=254)
    population_per_hospital = models.FloatField()
    catchment_area_hospital = models.FloatField()
    nightlight = models.IntegerField(null=True)

    district = models.ForeignKey("District", on_delete=models.CASCADE, related_name="simulated_hospitals", null=True)

    objects = models.Manager()
    vector_tiles = MVTManager(columns=["id", "population_per_hospital", "catchment_area_hospital"])

    filters = ["population_per_hospital", "catchment_area_hospital"]

    data_file = "HealthCare_Infrastructure"
    layer = "Gha_HealthCareFacilities_SelectedSites"
    mapping = {
        "geom": "POINT",
        "name": "FacilityNa",
        "type": "Type",
        "town": "Town",
        "ownership": "Ownership",
        "population_per_hospital": "Pop_per_hosp",
        "catchment_area_hospital": "Catchment_area_hosp",
        "nightlight": "nightlight_digitalNumber",
    }
