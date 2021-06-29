import os

from config.settings.base import ROOT_DIR
from enershelf.utils.ogr_layer_mapping import RelatedModelLayerMapping
from enershelf.map.models import Region, District, Hospitals, HospitalsSimulated, Cluster, Nightlight


MODELS = [
    Region,
    District,
    Hospitals,
    HospitalsSimulated,
    Cluster,
    Nightlight,
]


def load_data(models=None, verbose=True):
    models = models or MODELS
    for model in models:
        print(f"Upload data for model '{model.__name__}'")
        instance = RelatedModelLayerMapping(
            model=model,
            data=os.path.join(ROOT_DIR, "enershelf", "data", f"{model.data_file}.gpkg",),
            mapping=model.mapping,
            layer=model.layer,
            transform=4326,
        )
        instance.save(strict=True, verbose=verbose)


def empty_data(models=None):
    models = models or MODELS
    for model in models:
        model.objects.all().delete()
