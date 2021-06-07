import json
import pathlib
from collections import namedtuple

from range_key_dict import RangeKeyDict

from django.conf import settings
from enershelf import __version__

# REGIONS

MIN_ZOOM = 4
MAX_ZOOM = 22
MAX_DISTILLED_ZOOM = 10

Zoom = namedtuple("MinMax", ["min", "max"])
ZOOM_LEVELS = {
    # "country": Zoom(MIN_ZOOM, 5),
    # "state": Zoom(5, 8),
    "district": Zoom(MIN_ZOOM, MAX_ZOOM),
    # "municipality": Zoom(11, MAX_ZOOM + 1),
}
REGIONS = (
    # "country",
    # "state",
    "district",
    # "municipality",
)
REGION_ZOOMS = RangeKeyDict({zoom: layer for layer, zoom in ZOOM_LEVELS.items() if layer in REGIONS})


# FILTERS

FILTER_DEFINITION = {}


# STORE

STORE_COLD_INIT = json.dumps({"version": __version__})


def init_hot_store():
    # Filter booleans have to be stored as str:
    filter_init = {}
    for filter_, data in FILTER_DEFINITION.items():
        initial = data["initial"]
        if initial is True:
            initial = "True"
        elif initial is False:
            initial = "False"
        filter_init[data["js_event_name"]] = initial
    return json.dumps(filter_init)


STORE_HOT_INIT = init_hot_store()


# SOURCES


def init_sources():
    sources = {}
    metadata_path = pathlib.Path(settings.METADATA_DIR)
    for metafile in metadata_path.iterdir():
        with open(metafile, "r") as metadata_raw:
            metadata = json.loads(metadata_raw.read())
            sources[metadata["id"]] = metadata
    return sources


SOURCES = init_sources()


# MAP

MAP_IMAGES = {"hospital": "images/icons/hospital.png"}


# DISTILL

# Tiles of Germany: At z=4 Germany has width x=8-9 and height y=5-6
X_AT_MIN_Z = 8
Y_AT_MIN_Z = 5


def get_tile_coordinates_for_region(region):
    for z in range(MIN_ZOOM, MAX_DISTILLED_ZOOM + 1):
        z_factor = 2 ** (z - MIN_ZOOM)
        for x in range(X_AT_MIN_Z * z_factor, (X_AT_MIN_Z + 1) * z_factor):
            for y in range(Y_AT_MIN_Z * z_factor, (Y_AT_MIN_Z + 1) * z_factor):
                if region in REGIONS and REGION_ZOOMS[z] != region:
                    continue
                yield x, y, z
