"""Configuration for map app."""
import json
import pathlib
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from digiplan import __version__

from . import datapackage, utils

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


def get_slider_marks() -> dict:
    """
    get all status quo values and future scenario values for all settings.

    Returns
    -------
    dict
        one dict with all values in correct format for usage
    """
    all_settings = get_all_settings().items()
    slider_marks = {}
    for param_name, param_data in all_settings:
        if "status_quo" in param_data:
            if param_name in slider_marks:
                slider_marks[param_name].append(("Heute", param_data["status_quo"]))
            else:
                slider_marks[param_name] = [("Heute", param_data["status_quo"])]
        if "future_scenario" in param_data:
            if param_name in slider_marks:
                slider_marks[param_name].append(("2045", param_data["future_scenario"]))
            else:
                slider_marks[param_name] = [("2045", param_data["future_scenario"])]
    return slider_marks


def get_slider_per_sector() -> dict:
    """
    get demand per sector.

    Returns
    -------
    dict
        demand per sector for each slider
    """
    sector_dict = {
        "s_v_1": {"hh": 0, "ind": 0, "cts": 0},
        "w_v_1": {"hh": 0, "ind": 0, "cts": 0},
        "w_d_wp_1": {"hh": 0, "ind": 0, "cts": 0},
    }
    demand = {"s_v_1": "power_demand", "w_v_1": "heat_demand", "w_d_wp_1": "heat_demand_dec"}
    sectors = ["hh", "ind", "cts"]
    for key, value in demand.items():
        for sector in sectors:
            file = f"demand_{sector}_{value}.csv"
            path = Path(settings.DATA_DIR, "digipipe/scalars", file)
            reader = pd.read_csv(path)
            sector_dict[key][sector] = reader["2022"].sum()
    return sector_dict


# STORE
STORE_COLD_INIT = {
    "version": __version__,
    "slider_marks": get_slider_marks(),
    "slider_max": datapackage.get_potential_values(),
    "slider_per_sector": get_slider_per_sector(),
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
    "ABW-solar-pv_ground": _("Ground-mounted PV"),
    "ABW-solar-pv_rooftop": _("Roof-mounted PV"),
    "ABW-wind-onshore": _("Wind turbine"),
    "ABW-hydro-ror": _("Hydro"),
    "ABW-biomass": _("Biomass"),
    "ABW-electricity-import": _("Import"),
}

SIMULATION_DEMANDS = {
    # electricty demands
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
