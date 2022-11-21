import json
import pathlib
from collections import namedtuple

import colorbrewer
from django.conf import settings
from range_key_dict import RangeKeyDict

from digiplan import __version__

# FILES

STYLES_DIR = settings.APPS_DIR.path("static").path("styles")

CLUSTER_GEOJSON_FILE = settings.DATA_DIR.path("cluster.geojson")
LAYER_STYLES_FILE = STYLES_DIR.path("layer_styles.json")
RESULT_STYLES_FILE = STYLES_DIR.path("result_styles.json")
CHOROPLETH_STYLES_FILE = STYLES_DIR.path("choropleth_styles.json")
PARAMETERS_FILE = pathlib.Path(__file__).parent / "parameters.json"

# REGIONS

MIN_ZOOM = 6
MAX_ZOOM = 22
MAX_DISTILLED_ZOOM = 10

Zoom = namedtuple("MinMax", ["min", "max"])
ZOOM_LEVELS = {
    "municipality": Zoom(8, MAX_ZOOM),
}
REGIONS = ("municipality",)
REGION_ZOOMS = RangeKeyDict({zoom: layer for layer, zoom in ZOOM_LEVELS.items() if layer in REGIONS})


# FILTERS

FILTER_DEFINITION = {}
REGION_FILTER_LAYERS = ["built_up_areas", "settlements", "hospitals"]


# PARAMETERS

with open(PARAMETERS_FILE, "r", encoding="utf-8") as param_file:
    PARAMETERS = json.load(param_file)


# STORE

STORE_COLD_INIT = {
    "version": __version__,
    "debugMode": settings.DEBUG,
    "zoom_levels": ZOOM_LEVELS,
    "region_filter_layers": REGION_FILTER_LAYERS,
    "slider_marks": {
        param_name: [("Status Quo", param_data["status_quo"])]
        for param_name, param_data in PARAMETERS.items()
        if "status_quo" in param_data
    },
}


def init_hot_store():
    # Filter booleans have to be stored as str:
    filter_init = {data["js_event_name"]: "True" if data["initial"] else "False" for data in FILTER_DEFINITION.values()}
    return json.dumps(filter_init)


STORE_HOT_INIT = init_hot_store()


# SOURCES


def init_sources():
    sources = {}
    metadata_path = pathlib.Path(settings.METADATA_DIR)
    for metafile in metadata_path.iterdir():
        if metafile.suffix != ".json":
            continue
        with open(metafile, "r", encoding="utf-8") as metadata_raw:
            metadata = json.loads(metadata_raw.read())
            sources[metadata["id"]] = metadata
    return sources


SOURCES = init_sources()


# STYLES

CHOROPLETH_STYLES = {}
with open(CHOROPLETH_STYLES_FILE, mode="r", encoding="utf-8") as choropleth_styles_file:
    choropleths = json.load(choropleth_styles_file)
    for name, choropleth_config in choropleths.items():
        if choropleth_config["color_palette"] not in colorbrewer.sequential["multihue"]:
            raise KeyError(f"Invalid color palette for choropleth {name=}.")
        if len(choropleth_config["values"]) > 6:
            raise IndexError(f"Too many choropleth values given for {name=}.")
        colors = colorbrewer.sequential["multihue"][choropleth_config["color_palette"]][
            len(choropleth_config["values"])
        ]
        fill_color = [
            "interpolate",
            ["linear"],
            ["feature-state", name],
        ]
        for value, color in zip(choropleth_config["values"], colors):
            fill_color.append(value)
            rgb_color = f"rgb({color[0]}, {color[1]}, {color[2]})"
            fill_color.append(rgb_color)
        CHOROPLETH_STYLES[name] = fill_color

with open(LAYER_STYLES_FILE, mode="r", encoding="utf-8") as layer_styles_file:
    LAYER_STYLES = json.load(layer_styles_file)

with open(RESULT_STYLES_FILE, mode="r", encoding="utf-8") as result_styles_file:
    RESULT_STYLES = json.load(result_styles_file)
RESULT_STYLES.update(CHOROPLETH_STYLES)


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
