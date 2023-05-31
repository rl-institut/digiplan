"""Module for extracting structure and data for charts."""

import json
import pathlib
from collections import namedtuple
from collections.abc import Callable, Iterable
from typing import Optional

import pandas as pd

from digiplan.map import calculations, config, models

Chart = namedtuple("Chart", ("lookup", "div_id"))

RESULT_CHARTS = (Chart("detailed_overview", "detailed_overview_chart"),)

CHARTS: dict[str, Callable] = {
    "capacity": calculations.capacity_chart,
    "capacity_square": calculations.capacity_square_chart,
    "population": models.Population.population_history,
    "population_density": models.Population.density_history,
    "wind_turbines": models.WindTurbine.wind_turbines_history,
    "wind_turbines_square": models.WindTurbine.wind_turbines_per_area_history,
    "detailed_overview": calculations.detailed_overview,
}


def get_chart_options(lookup: str) -> dict:
    """
    Get the options for a chart from the corresponding json file.

    Parameters
    ----------
    lookup: str
        Looks up related chart function in CHARTS

    Returns
    -------
    dict
        Containing the json that can be filled with data

    Raises
    ------
    LookupError
        if lookup can't be found in LOOKUPS
    """
    lookup_path = pathlib.Path(config.CHARTS_DIR.path(f"{lookup}.json"))
    if not lookup_path.exists():
        error_msg = f"Could not find {lookup=} in charts folder."
        raise LookupError(error_msg)

    with lookup_path.open("r", encoding="utf-8") as lookup_json:
        lookup_options = json.load(lookup_json)

    with pathlib.Path(config.CHARTS_DIR.path("general_options.json")).open("r", encoding="utf-8") as general_chart_json:
        general_chart_options = json.load(general_chart_json)

    chart = merge_dicts(general_chart_options, lookup_options)

    return chart


def create_chart(lookup: str, chart_data: Optional[Iterable[tuple[str, float]]] = None) -> dict:
    """
    Create chart based on given lookup and municipality ID or result option.

    Parameters
    ----------
    lookup: str
        Looks up related chart function in charts folder.
    chart_data: list[tuple[str, float]]
        Chart data separated into tuples holding key and value
        If no data is given, data is expected to be set via lookup JSON

    Returns
    -------
    dict
        Containing chart filled with data

    """
    chart = get_chart_options(lookup)
    if chart_data:
        series_type = chart["series"][0]["type"]
        series_length = len(chart["series"])
        if series_type == "line":
            data = []
            for key, value in chart_data:
                year_as_string = f"{key}"
                data.append([year_as_string, value])
            chart["series"][0]["data"] = data
        elif series_length > 1:
            for i in range(0, series_length):
                chart["series"][i]["data"] = chart_data[i]
        else:
            chart["series"][0]["data"] = chart_data

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
