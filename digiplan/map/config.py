"""Configuration for map app."""
import json
import pathlib

from django.conf import settings

from digiplan import __version__

from . import utils

# DIRECTORIES
MAP_DIR = settings.APPS_DIR.path("map")
POPUPS_DIR = MAP_DIR.path("results").path("popups")
SCENARIOS_DIR = settings.DATA_DIR.path("scenarios")
CHARTS_DIR = MAP_DIR.path("results").path("charts")

# FILES
ENERGY_SETTINGS_PANEL_FILE = settings.APPS_DIR.path("static/config/energy_settings_panel.json")
HEAT_SETTINGS_PANEL_FILE = settings.APPS_DIR.path("static/config/heat_settings_panel.json")
TRAFFIC_SETTINGS_PANEL_FILE = settings.APPS_DIR.path("static/config/traffic_settings_panel.json")
SETTINGS_DEPENDENCY_MAP_FILE = settings.APPS_DIR.path("static/config/settings_dependency_map.json")
DEPENDENCY_PARAMETERS_FILE = settings.APPS_DIR.path("static/config/dependency_parameters.json")

# FILTERS
FILTER_DEFINITION = {}
REGION_FILTER_LAYERS = []

# PARAMETERS
ENERGY_SETTINGS_PANEL = utils.get_translated_json_from_file(ENERGY_SETTINGS_PANEL_FILE)
HEAT_SETTINGS_PANEL = utils.get_translated_json_from_file(HEAT_SETTINGS_PANEL_FILE)
TRAFFIC_SETTINGS_PANEL = utils.get_translated_json_from_file(TRAFFIC_SETTINGS_PANEL_FILE)
SETTINGS_DEPENDENCY_MAP = utils.get_translated_json_from_file(SETTINGS_DEPENDENCY_MAP_FILE)
DEPENDENCY_PARAMETERS = utils.get_translated_json_from_file(DEPENDENCY_PARAMETERS_FILE)


# STORE
STORE_COLD_INIT = {
    "version": __version__,
    "slider_marks": {
        param_name: [("Status Quo", param_data["status_quo"])]
        for param_name, param_data in ENERGY_SETTINGS_PANEL.items()
        if "status_quo" in param_data
    },
    "allowedSwitches": ["wind_distance"],
    "detailTab": {"showPotentialLayers": True},
    "staticState": 0,
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
