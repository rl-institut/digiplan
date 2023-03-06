"""Configuration for map app."""

import json
import pathlib
from collections import namedtuple

from django.conf import settings
from range_key_dict import RangeKeyDict

from config.settings.base import APPS_DIR
from digiplan import __version__
from digiplan.map.mapset import choropleth

# DIRECTORIES
MAP_DIR = APPS_DIR.path("map")
POPUPS_DIR = MAP_DIR.path("results").path("popups")

# FILES
CLUSTER_GEOJSON_FILE = settings.DATA_DIR.path("cluster.geojson")
LAYER_STYLES_FILE = settings.APPS_DIR.path("static/config/layer_styles.json")
CHOROPLETHS_FILE = settings.APPS_DIR.path("static/config/choropleths.json")
ENERGY_SETTINGS_PANEL_FILE = settings.APPS_DIR.path("static/config/energy_settings_panel.json")
HEAT_SETTINGS_PANEL_FILE = settings.APPS_DIR.path("static/config/heat_settings_panel.json")
TRAFFIC_SETTINGS_PANEL_FILE = settings.APPS_DIR.path("static/config/traffic_settings_panel.json")
SETTINGS_DEPENDENCY_MAP_FILE = settings.APPS_DIR.path("static/config/settings_dependency_map.json")
DEPENDENCY_PARAMETERS_FILE = settings.APPS_DIR.path("static/config/dependency_parameters.json")

# REGIONS
MIN_ZOOM = 8
MAX_ZOOM = 22
MAX_DISTILLED_ZOOM = 10
DEFAULT_CLUSTER_ZOOM = 11

Zoom = namedtuple("MinMax", ["min", "max"])
ZOOM_LEVELS = {
    "municipality": Zoom(MIN_ZOOM, MAX_ZOOM),
}
REGIONS = ("municipality",)
REGION_ZOOMS = RangeKeyDict({zoom: layer for layer, zoom in ZOOM_LEVELS.items() if layer in REGIONS})

# FILTERS
FILTER_DEFINITION = {}
REGION_FILTER_LAYERS = ["built_up_areas", "settlements", "hospitals"]

# PARAMETERS
with pathlib.Path(ENERGY_SETTINGS_PANEL_FILE).open("r", encoding="utf-8") as param_file:
    ENERGY_SETTINGS_PANEL = json.load(param_file)

with pathlib.Path(HEAT_SETTINGS_PANEL_FILE).open("r", encoding="utf-8") as param_file:
    HEAT_SETTINGS_PANEL = json.load(param_file)

with pathlib.Path(TRAFFIC_SETTINGS_PANEL_FILE).open("r", encoding="utf-8") as param_file:
    TRAFFIC_SETTINGS_PANEL = json.load(param_file)

with pathlib.Path(SETTINGS_DEPENDENCY_MAP_FILE).open("r", encoding="utf-8") as param_file:
    SETTINGS_DEPENDENCY_MAP = json.load(param_file)

with pathlib.Path(DEPENDENCY_PARAMETERS_FILE).open("r", encoding="utf-8") as param_file:
    DEPENDENCY_PARAMETERS = json.load(param_file)


# STORE
STORE_COLD_INIT = {
    "version": __version__,
    "debugMode": settings.DEBUG,
    "zoom_levels": ZOOM_LEVELS,
    "region_filter_layers": REGION_FILTER_LAYERS,
    "slider_marks": {
        param_name: [("Status Quo", param_data["status_quo"])]
        for param_name, param_data in ENERGY_SETTINGS_PANEL.items()
        if "status_quo" in param_data
    },
}


def init_hot_store() -> str:
    """Initialize hot store for use in JS store.

    Returns
    -------
    str
        Hot store as json literal
    """
    # Filter booleans have to be stored as str:
    filter_init = {data["js_event_name"]: "True" if data["initial"] else "False" for data in FILTER_DEFINITION.values()}
    return json.dumps(filter_init)


STORE_HOT_INIT = init_hot_store()


# SOURCES
def init_sources() -> dict[str, dict]:
    """Initialize sources to be shown in sources section in app.

    Returns
    -------
    dict
        holding metadata of source as value and metadata ID as key.
    """
    sources = {}
    metadata_path = pathlib.Path(settings.METADATA_DIR)
    for metafile in metadata_path.iterdir():
        if metafile.suffix != ".json":
            continue
        with pathlib.Path(metafile).open("r", encoding="utf-8") as metadata_raw:
            metadata = json.loads(metadata_raw.read())
            sources[metadata["id"]] = metadata
    return sources


SOURCES = init_sources()


# STYLES
CHOROPLETHS = choropleth.Choropleth(CHOROPLETHS_FILE)

with pathlib.Path(LAYER_STYLES_FILE).open("r", encoding="utf-8") as layer_styles_file:
    LAYER_STYLES = json.load(layer_styles_file)
LAYER_STYLES.update(CHOROPLETHS.get_static_styles())


# MAP
MapImage = namedtuple("MapImage", ["name", "path"])
MAP_IMAGES = []


# DISTILL
X_AT_MIN_Z = 136
Y_AT_MIN_Z = 84
X_OFFSET = 1  # Defines how many tiles to the right are added at first level
Y_OFFSET = 1  # Defines how many tiles to the bottom are added at first level


def get_tile_coordinates_for_region(region: str) -> tuple[int, int, int]:
    """Return x,y,z coordinates for each layer in order to distill it.

    Parameters
    ----------
    region: str
        Region/layer to get tile coordinates for

    Yields
    ------
    tuple[int, int, int]
        Holding x,y,z
    """
    for z in range(MIN_ZOOM, MAX_DISTILLED_ZOOM + 1):
        z_factor = 2 ** (z - MIN_ZOOM)
        for x in range(X_AT_MIN_Z * z_factor, (X_AT_MIN_Z + 1) * z_factor + X_OFFSET):
            for y in range(Y_AT_MIN_Z * z_factor, (Y_AT_MIN_Z + 1) * z_factor + Y_OFFSET):
                if region in REGIONS and REGION_ZOOMS[z] != region:
                    continue
                yield x, y, z
