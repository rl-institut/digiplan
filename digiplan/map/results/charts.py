"""Module for extracting structure and data for charts."""

import json
import pathlib
from collections import namedtuple
from functools import partial

import jsonschema

from config import schemas
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
    "detailed_overview_chart",
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
        with pathlib.Path(config.CHARTS_DIR.path(f"{lookup}_chart.json")).open("r", encoding="utf-8") as chart_json:
            chart = json.load(chart_json)

        with pathlib.Path(config.CHARTS_DIR.path("general_options.json")).open("r", encoding="utf-8") as options_json:
            options = json.load(options_json)
    else:
        error_msg = f"Could not find {lookup=} in POPUPCHARTS or RESULTCHARTS."
        raise LookupError(error_msg)

    # space to modify options if needed

    chart.update(options)

    return chart


def get_chart_data(lookup: str, municipality_id: int) -> dict:
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

    jsonschema.validate(chart, schemas.CHART_SCHEMA)
    return chart


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
