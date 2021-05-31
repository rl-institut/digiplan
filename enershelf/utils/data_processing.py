import os
from django.contrib.gis.utils import LayerMapping

from config.settings.base import ROOT_DIR
from enershelf.map.models import District, Grid


MODELS = [District, Grid]


def load_data(models=None, verbose=True):
    models = models or MODELS
    for model in models:
        instance = LayerMapping(
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
