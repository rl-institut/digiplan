import json
import os

from geojson import Feature, FeatureCollection, Point
from raster.models import Legend
from raster.models import RasterLayer as RasterModel

from config.settings.base import DATA_DIR
from digiplan.map.config.config import CLUSTER_GEOJSON_FILE, LAYER_STYLES, ZOOM_LEVELS
from digiplan.map.layers import LAYERS_DEFINITION, VectorLayerData
from digiplan.map.models import Municipality, Region, WindTurbine
from digiplan.utils.ogr_layer_mapping import RelatedModelLayerMapping

REGIONS = [Municipality]

MODELS = [WindTurbine]


def load_regions(regions=None, verbose=True):
    regions = regions or REGIONS
    for region in regions:
        if region.objects.exists():
            print(f"Skipping data for model '{region.__name__}' - Please empty model first if you want to update data.")
            continue
        print(f"Upload data for region '{region.__name__}'")
        if hasattr(region, "data_folder"):
            data_path = os.path.join(DATA_DIR, region.data_folder, f"{region.data_file}.gpkg")
        else:
            data_path = os.path.join(DATA_DIR, f"{region.data_file}.gpkg")
        region_model = Region(layer_type=region.__name__.lower())
        region_model.save()
        instance = RelatedModelLayerMapping(
            model=region,
            data=data_path,
            mapping=region.mapping,
            layer=region.layer,
            transform=4326,
        )
        instance.region = region_model
        instance.save(strict=True, verbose=verbose)


def load_data(models=None):
    models = models or MODELS
    for model in models:
        if model.objects.exists():
            print(f"Skipping data for model '{model.__name__}' - Please empty model first if you want to update data.")
            continue
        print(f"Upload data for model '{model.__name__}'")
        if hasattr(model, "data_folder"):
            data_path = os.path.join(DATA_DIR, model.data_folder, f"{model.data_file}.gpkg")
        else:
            data_path = os.path.join(DATA_DIR, f"{model.data_file}.gpkg")
        instance = RelatedModelLayerMapping(
            model=model,
            data=data_path,
            mapping=model.mapping,
            layer=model.layer,
            transform=4326,
        )
        instance.save(strict=True)


def load_raster(layers=None):
    layers = layers or LAYERS_DEFINITION
    for layer in layers:
        if not issubclass(layer.model, RasterModel):
            continue
        if RasterModel.objects.filter(name=layer.source).exists():
            print(f"Skipping data for raster '{layer.name}' - Please empty raster first if you want to update data.")
            continue
        print(f"Upload data for raster '{layer.name}'")
        rm = RasterModel(name=layer.source, rasterfile=layer.filepath)
        rm.save()
        if Legend.objects.filter(title=layer.legend).exists():
            print(
                f"Skipping legend '{layer.legend}' for raster '{layer.name}' - "
                f"Please remove raster legend first if you want to update it."
            )
            continue
        legend = Legend(title=layer.legend, json=json.dumps(LAYER_STYLES[layer.legend]))
        legend.save()


def build_cluster_geojson(cluster_layers: list[VectorLayerData] = None):
    cluster_layers = cluster_layers or LAYERS_DEFINITION
    features = []
    for region_model in REGIONS:
        region_name = region_model.__name__.lower()
        zoom_level = ZOOM_LEVELS[region_name].max
        for region in region_model.objects.all():
            point = Point(region.geom.point_on_surface.coords)
            properties = {"zoom_level": zoom_level}
            for cluster_layer in cluster_layers:
                if not hasattr(cluster_layer, "clustered") or not cluster_layer.clustered:
                    continue
                cluster_count = len(cluster_layer.model.objects.filter(geom__within=region.geom))
                properties[cluster_layer.source] = cluster_count
            feature = Feature(geometry=point, properties=properties)
            features.append(feature)
    fc = FeatureCollection(features)
    with open(CLUSTER_GEOJSON_FILE, "w", encoding="utf-8") as geojson_file:
        json.dump(fc, geojson_file)


def empty_data(models=None):
    models = models or MODELS
    for model in models:
        model.objects.all().delete()


def empty_raster(layers=None):
    layers = layers or LAYERS_DEFINITION
    for layer in layers:
        if not issubclass(layer.model, RasterModel):
            continue
        RasterModel.objects.filter(name=layer.source).delete()
        Legend.objects.filter(title=layer.legend).delete()
