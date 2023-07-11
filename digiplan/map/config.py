"""Configuration for map app."""
import json
import pathlib

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from digiplan import __version__

from . import area, utils

# DIRECTORIES
MAP_DIR = settings.APPS_DIR.path("map")
CHARTS_DIR = MAP_DIR.path("charts")
SCENARIOS_DIR = settings.DATA_DIR.path("scenarios")

# FILES
ENERGY_SETTINGS_PANEL_FILE = settings.APPS_DIR.path("static/config/energy_settings_panel.json")
HEAT_SETTINGS_PANEL_FILE = settings.APPS_DIR.path("static/config/heat_settings_panel.json")
TRAFFIC_SETTINGS_PANEL_FILE = settings.APPS_DIR.path("static/config/traffic_settings_panel.json")
ADDITIONAL_ENERGY_SETTINGS_FILE = settings.DATA_DIR.path("digipipe/settings/energy_settings_panel.json")
ADDITIONAL_HEAT_SETTINGS_FILE = settings.DATA_DIR.path("digipipe/settings/heat_settings_panel.json")
ADDITIONAL_TRAFFIC_SETTINGS_FILE = settings.DATA_DIR.path("digipipe/settings/traffic_settings_panel.json")
SETTINGS_DEPENDENCY_MAP_FILE = settings.APPS_DIR.path("static/config/settings_dependency_map.json")
DEPENDENCY_PARAMETERS_FILE = settings.APPS_DIR.path("static/config/dependency_parameters.json")
TECHNOLOGY_DATA_FILE = settings.DIGIPIPE_DIR.path("scalars").path("technology_data.json")

# FILTERS
FILTER_DEFINITION = {}
REGION_FILTER_LAYERS = []

# PARAMETERS
ENERGY_SETTINGS_PANEL = utils.get_translated_json_from_file(ENERGY_SETTINGS_PANEL_FILE)
HEAT_SETTINGS_PANEL = utils.get_translated_json_from_file(HEAT_SETTINGS_PANEL_FILE)
TRAFFIC_SETTINGS_PANEL = utils.get_translated_json_from_file(TRAFFIC_SETTINGS_PANEL_FILE)
ADDITIONAL_ENERGY_SETTINGS = utils.get_translated_json_from_file(ADDITIONAL_ENERGY_SETTINGS_FILE)
ADDITIONAL_HEAT_SETTINGS = utils.get_translated_json_from_file(ADDITIONAL_HEAT_SETTINGS_FILE)
ADDITIONAL_TRAFFIC_SETTINGS = utils.get_translated_json_from_file(ADDITIONAL_TRAFFIC_SETTINGS_FILE)
SETTINGS_DEPENDENCY_MAP = utils.get_translated_json_from_file(SETTINGS_DEPENDENCY_MAP_FILE)
DEPENDENCY_PARAMETERS = utils.get_translated_json_from_file(DEPENDENCY_PARAMETERS_FILE)
TECHNOLOGY_DATA = utils.get_translated_json_from_file(TECHNOLOGY_DATA_FILE)


def get_all_settings() -> dict:
    """
    Concatenate all Settings.

    Returns
    -------
    dict
        one dict with all settings concatenated
    """
    all_settings = {}
    for setting_dict in [
        ENERGY_SETTINGS_PANEL,
        HEAT_SETTINGS_PANEL,
        TRAFFIC_SETTINGS_PANEL,
        ADDITIONAL_ENERGY_SETTINGS,
        ADDITIONAL_HEAT_SETTINGS,
        ADDITIONAL_TRAFFIC_SETTINGS,
    ]:
        all_settings.update(setting_dict)
    return all_settings


# STORE
STORE_COLD_INIT = {
    "version": __version__,
    "slider_marks": {
        param_name: [("Status Quo", param_data["status_quo"])]
        for param_name, param_data in get_all_settings().items()
        if "status_quo" in param_data
    },
    "slider_max": area.get_max_values(),
    "allowedSwitches": ["wind_distance"],
    "detailTab": {"showPotentialLayers": True},
    "staticState": 0,
}


def init_hot_store() -> str:
    """
    Initialize hot store for use in JS store.

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
    """
    Initialize sources to be shown in sources section in app.

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


# SIMULATION

SIMULATION_RENEWABLES = {
    "ABW-solar-pv_ground": _("Outdoor PV"),
    "ABW-solar-pv_rooftop": _("Roof-mounted PV"),
    "ABW-wind-onshore": _("Wind turbine"),
    "ABW-hydro-ror": _("Hydro"),
    "ABW-biomass": _("Biomass"),
}

SIMULATION_DEMANDS = {
    # electricty demands
    "ABW-electricity-bev_charging": _("BEV"),
    "ABW-electricity-demand_hh": _("Electricity Household Demand"),
    "ABW-electricity-demand_cts": _("Electricity CTS Demand"),
    "ABW-electricity-demand_ind": _("Electricity Industry Demand"),
    "electricity_heat_demand_hh": _("Electricity Household Heat Demand"),
    "electricity_heat_demand_cts": _("Electricity CTS Heat Demand"),
    "electricity_heat_demand_ind": _("Electricity Industry Heat Demand"),
    # heat demands
    "heat-demand-cts": _("CTS Heat Demand"),
    "heat-demand-hh": _("Household Heat Demand"),
    "heat-demand-ind": _("Industry Heat Demand"),
}

SIMULATION_NAME_MAPPING = {} | SIMULATION_RENEWABLES | SIMULATION_DEMANDS
