"""Module for extracting structure and data for charts."""

import json
import pathlib
from collections import namedtuple
from functools import partial

from digiplan.map import config, models

POPUPCHARTS = (
    "capacity",
    "capacity_square",
    "population",
    "population_density",
    "wind_turbines",
    "wind_turbines_square",
)

RESULTCHARTS = (
    "detailed_overview",
    "ghg_overview_chart",
    "electricity_overview_chart",
    "electricity_THG_chart",
    "mobility_overview_chart",
    "mobility_THG_chart",
)

LookupFunctions = namedtuple("PopupData", ("data_fct", "chart_fct", "choropleth_fct"))


def get_chart_structure(lookup: str) -> json:
    """Get the structure and options for a chart from the coresponding json file.

    Parameters
    ----------
    lookup: str
        Looks up related chart function in POPUPCHARTS or RESULTCHARTS.

    Returns
    -------
    json
        Containing the json that can be filled with data

    Raises
    ------
    LookupError
        if lookup can't be found in LOOKUPS
    """

    if lookup in POPUPCHARTS:
        with pathlib.Path(config.POPUPS_DIR.path(f"{lookup}_chart.json")).open("r", encoding="utf-8") as chart_json:
            chart = json.load(chart_json)

        with pathlib.Path(config.POPUPS_DIR.path("general_options.json")).open("r", encoding="utf-8") as options_json:
            options = json.load(options_json)
    elif lookup in RESULTCHARTS:
        with pathlib.Path(config.CHARTS_DIR.path(f"{lookup}.json")).open("r", encoding="utf-8") as chart_json:
            chart = json.load(chart_json)

        with pathlib.Path(config.CHARTS_DIR.path("general_options.json")).open("r", encoding="utf-8") as options_json:
            options = json.load(options_json)
    else:
        error_msg = f"Could not find {lookup=} in POPUPCHARTS or RESULTCHARTS."
        raise LookupError(error_msg)

    # space to modify options if needed

    chart = merge_dicts(chart, options)

    return chart


def create_chart(lookup: str, municipality_id: int) -> dict:
    """Create chart based on given lookup and municipality ID or result option

    Parameters
    ----------
    lookup: str
        Looks up related chart function in POPUPCHARTS or RESULTCHARTS.

    Returns
    -------
    dict
        Containing chart filled with data

    """
    chart = get_chart_structure(lookup)
    if lookup in POPUPCHARTS:
        # maybe get popupchart data through calculations.py?
        chart_data = LOOKUPS[lookup].chart_fct(municipality_id)
        chart["series"][0]["data"] = [{"key": key, "value": value} for key, value in chart_data]

    # space to add result chart data dynamically
    print(chart)
    # jsonschema.validate(chart, schemas.CHART_SCHEMA)
    return chart


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Recursively merge two dictionaries.

    Parameters
    ----------
    dict1: dict
        Containing the first chart structure. Objects will be first.
    dict2: dict
        Containing the second chart structure. Objects will be last and
        if they have the same name as ones from dict1 they overwrite the ones in first.

    Returns
    -------
    dict
        First chart modified and appended by second chart.
    """
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            merge_dicts(dict1[key], dict2[key])
        elif key in dict1 and isinstance(dict1[key], list) and isinstance(dict2[key], list):
            dict1[key].extend(dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1


LOOKUPS: dict[str, LookupFunctions] = {
    "population": LookupFunctions(
        partial(models.Population.quantity, year=2022),
        models.Population.population_history,
        models.Population.population_per_municipality,
    ),
    "population_density": LookupFunctions(
        partial(models.Population.density, year=2022),
        models.Population.density_history,
        models.Population.denisty_per_municipality,
    ),
    "wind_turbines": LookupFunctions(
        models.WindTurbine.quantity,
        models.WindTurbine.wind_turbines_history,
        models.WindTurbine.quantity_per_municipality,
    ),
    "wind_turbines_square": LookupFunctions(
        models.WindTurbine.quantity_per_square,
        models.WindTurbine.wind_turbines_per_area_history,
        models.WindTurbine.quantity_per_mun_and_area,
    ),
}
