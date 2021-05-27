import os
from django.contrib.gis.utils import LayerMapping

from config.settings.base import ROOT_DIR
from enershelf.map.models import District


def run(verbose=True):
    districts = LayerMapping(
        District,
        os.path.join(ROOT_DIR, "enershelf", "data", f"{District.data_file}.gpkg",),
        District.mapping,
        transform=4326,
    )
    districts.save(strict=True, verbose=verbose)
