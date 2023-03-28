"""Configuration for map app."""
import ast
import json
import pathlib

from django.conf import settings
from django.template import Context, Template

from digiplan import __version__

# DIRECTORIES
MAP_DIR = settings.APPS_DIR.path("map")
POPUPS_DIR = MAP_DIR.path("results").path("popups")

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
with pathlib.Path(ENERGY_SETTINGS_PANEL_FILE).open("r", encoding="utf-8") as param_file:
    energy_settings_dict = json.load(param_file)
    # add {% load i18n %} to file to make django detect translatable strings
    t = Template("{% load i18n %}" + str(energy_settings_dict))
    # load context with the current language
    c = Context({})
    # translate (=render) dict, it becomes thereby a "django.utils.safestring"
    safe_string = t.render(c)
    # reconvert safestring to dict (needed later on)
    ENERGY_SETTINGS_PANEL = ast.literal_eval(safe_string)

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
