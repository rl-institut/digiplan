import os

from raster.models import RasterLayer as RasterModel

from config.settings.base import ROOT_DIR
from enershelf.utils.ogr_layer_mapping import RelatedModelLayerMapping
from enershelf.map.models import (
    Region,
    Country,
    State,
    District,
    Hospitals,
    BuiltUpAreas,
    Settlements,
    Hamlets,
    Nightlight,
)
from enershelf.map.layers import LAYERS_DEFINITION

REGIONS = [
    Country,
    State,
    District,
]

MODELS = [
    Hospitals,
    BuiltUpAreas,
    Settlements,
    Hamlets,
    Nightlight,
]


def load_regions(regions=None, verbose=True):
    regions = regions or REGIONS
    for region in regions:
        if region.objects.exists():
            print(f"Skipping data for model '{region.__name__}' - Please empty model first if you want to update data.")
            continue
        print(f"Upload data for region '{region.__name__}'")
        if hasattr(region, "data_folder"):
            data_path = os.path.join(ROOT_DIR, "enershelf", "data", region.data_folder, f"{region.data_file}.gpkg")
        else:
            data_path = os.path.join(ROOT_DIR, "enershelf", "data", f"{region.data_file}.gpkg")
        region_model = Region(layer_type=region.__name__.lower())
        region_model.save()
        instance = RelatedModelLayerMapping(
            model=region, data=data_path, mapping=region.mapping, layer=region.layer, transform=4326,
        )
        instance.region = region_model
        instance.save(strict=True, verbose=verbose)


def load_data(models=None, verbose=True):
    models = models or MODELS
    for model in models:
        if model.objects.exists():
            print(f"Skipping data for model '{model.__name__}' - Please empty model first if you want to update data.")
            continue
        print(f"Upload data for model '{model.__name__}'")
        if hasattr(model, "data_folder"):
            data_path = os.path.join(ROOT_DIR, "enershelf", "data", model.data_folder, f"{model.data_file}.gpkg")
        else:
            data_path = os.path.join(ROOT_DIR, "enershelf", "data", f"{model.data_file}.gpkg")
        instance = RelatedModelLayerMapping(
            model=model, data=data_path, mapping=model.mapping, layer=model.layer, transform=4326,
        )
        instance.save(strict=True, verbose=verbose)


def load_raster(layers=LAYERS_DEFINITION):
    for layer in layers:
        if not issubclass(layer["model"], RasterModel):
            continue
        RasterModel


def empty_data(models=None):
    models = models or MODELS
    for model in models:
        model.objects.all().delete()
