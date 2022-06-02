import os
import json
import pathlib
from collections import namedtuple

from range_key_dict import RangeKeyDict

from django.conf import settings
from digiplan import __version__


# FILES

CLUSTER_GEOJSON_FILE = settings.DATA_DIR.path("cluster.geojson")
LAYER_STYLES_FILE = os.path.join(os.path.dirname(__file__), "../static/styles/layer_styles.json")

# REGIONS

MIN_ZOOM = 6
MAX_ZOOM = 22
MAX_DISTILLED_ZOOM = 10

Zoom = namedtuple("MinMax", ["min", "max"])
ZOOM_LEVELS = {
    "country": Zoom(MIN_ZOOM, 7),
    "state": Zoom(7, 9),
    "district": Zoom(9, 11),
    "municipality": Zoom(11, MAX_ZOOM),
}
REGIONS = (
    "country",
    "state",
    "district",
    # "municipality",
)
REGION_ZOOMS = RangeKeyDict({zoom: layer for layer, zoom in ZOOM_LEVELS.items() if layer in REGIONS})


# FILTERS

FILTER_DEFINITION = {}
REGION_FILTER_LAYERS = ["built_up_areas", "settlements", "hospitals"]


# STORE

STORE_COLD_INIT = {
    "version": __version__,
    "debugMode": settings.DEBUG,
    "zoom_levels": ZOOM_LEVELS,
    "region_filter_layers": REGION_FILTER_LAYERS,
}


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


# STYLES

with open(
    LAYER_STYLES_FILE,
    mode="rb",
) as f:
    LAYER_STYLES = json.loads(f.read())


# MAP
MapImage = namedtuple("MapImage", ["name", "path"])
MAP_IMAGES = [MapImage("hospital", "images/icons/hospital.png")]


# DISTILL

# Tiles of Ghana: At z=5 Ghana has width x=15-16 and height y=15(-16)
X_AT_MIN_Z = 31
Y_AT_MIN_Z = 30
X_OFFSET = 1
Y_OFFSET = 1


def get_tile_coordinates_for_region(region):
    for z in range(MIN_ZOOM, MAX_DISTILLED_ZOOM + 1):
        z_factor = 2 ** (z - MIN_ZOOM)
        for x in range(X_AT_MIN_Z * z_factor, (X_AT_MIN_Z + 1) * z_factor + X_OFFSET):
            for y in range(Y_AT_MIN_Z * z_factor, (Y_AT_MIN_Z + 1) * z_factor + Y_OFFSET):
                if region in REGIONS and REGION_ZOOMS[z] != region:
                    continue
                yield x, y, z
