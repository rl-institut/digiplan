"""Module for calculations used for choropleths or charts."""

import json
import pathlib
from collections import namedtuple
from functools import partial
from typing import Optional

import jsonschema
from django.db.models import Sum

from config import schemas
from digiplan.map import config, models

LookupFunctions = namedtuple("PopupData", ("data_fct", "chart_fct", "choropleth_fct"))


def create_choropleth_data(lookup: str) -> dict:
    """Create data for every municipality for given lookup.

    Parameters
    ----------
    lookup: str
        Used to get function for choropleth data generation

    Returns
    -------
    dict
        Choropleth values for each municipality

    Raises
    ------
    LookupError
        if lookup can't be found in LOOKUPS
    """
    if lookup not in LOOKUPS:
        error_msg = f"Could not find {lookup=} in LOOKUPS."
        raise LookupError(error_msg)
    return LOOKUPS[lookup].choropleth_fct()


def create_chart(lookup: str, municipality_id: int) -> dict:
    """Create chart based on given lookup and municipality ID.

    Parameters
    ----------
    lookup: str
        Looks up related chart function in LOOKUPS.
    municipality_id: int
        Used to calculate chart data related to given municipality.

    Returns
    -------
    dict
        Containing validated chart options for further use in JS

    Raises
    ------
    LookupError
        if lookup can't be found in LOOKUPS
    """
    if lookup not in LOOKUPS:
        error_msg = f"Could not find {lookup=} in LOOKUPS."
        raise LookupError(error_msg)

    with pathlib.Path(config.POPUPS_DIR.path(f"{lookup}_chart.json")).open("r", encoding="utf-8") as chart_json:
        chart = json.load(chart_json)
    chart_data = LOOKUPS[lookup].chart_fct(municipality_id)
    chart["series"][0]["data"] = [{"key": key, "value": value} for key, value in chart_data]
    jsonschema.validate(chart, schemas.CHART_SCHEMA)
    return chart


def create_data(lookup: str, municipality_id: int) -> dict:
    """Create data for given lookup.

    Parameters
    ----------
    lookup: str
        Looks up related data function in LOOKUPS.
    municipality_id: int
        Used to calculate data related to given municipality.

    Returns
    -------
    dict
        containing popup data for given lookup

    Raises
    ------
    LookupError
        if lookup can't be found in LOOKUPS
    """
    if lookup not in LOOKUPS:
        error_msg = f"Could not find {lookup=} in LOOKUPS."
        raise LookupError(error_msg)

    with pathlib.Path(config.POPUPS_DIR.path(f"{lookup}.json")).open("r", encoding="utf-8") as data_json:
        data = json.load(data_json)

    data["id"] = municipality_id
    data["data"]["region_value"] = LOOKUPS[lookup].data_fct()
    data["data"]["municipality_value"] = LOOKUPS[lookup].data_fct(municipality_id=municipality_id)
    data["municipality"] = models.Municipality.objects.get(pk=municipality_id)

    return data


def calculate_square_for_value(value: int, municipality_id: int) -> float:
    area = 0.0
    if municipality_id is not None:
        area = models.Municipality.objects.get(pk=municipality_id).area
    else:
        for mun in models.Municipality.objects.all():
            area += models.Municipality.objects.get(pk=mun.id).area
    if area != 0.0:
        return value / area
    return value


def capacity_popup(municipality_id: Optional[int] = None) -> float:
    """Calculate capacity of renewables (either for municipality or for whole region).

    Parameters
    ----------
    municipality_id: Optional[int]
        If given, capacity of renewables for given municipality are calculated. If not, for whole region.

    Returns
    -------
    float
        Sum of installed renewables
    """
    capacity = 0.0
    values = capacity_choropleth()

    if municipality_id is not None:
        capacity = values[municipality_id]
    else:
        for _key, value in values.items():
            capacity += value
    return capacity


# pylint: disable=W0613
def capacity_chart(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
    """Get chart for capacity of renewables.

    Parameters
    ----------
    chart: dict
        Default chart options for capacity of renewables from JSON
    municipality_id: int
        Related municipality

    Returns
    -------
    dict
        Chart data to use in JS
    """
    chart["series"][0]["data"] = [{"key": 2023, "value": 2}, {"key": 2045, "value": 3}, {"key": 2050, "value": 4}]
    return chart


def capacity_choropleth() -> dict[int, int]:
    """Calculate capacity of renewables per municipality.

    Returns
    -------
    dict[int, int]
        Capacity per municipality
    """
    capacity = {}
    municipalities = models.Municipality.objects.all()

    for mun in municipalities:
        res_capacity = 0.0
        for renewable in models.RENEWABLES:
            one_capacity = renewable.objects.filter(mun_id__exact=mun.id).aggregate(Sum("capacity_net"))[
                "capacity_net__sum"
            ]
            if one_capacity is None:
                one_capacity = 0.0
            res_capacity += one_capacity
            capacity[mun.id] = res_capacity
    return capacity


def capacity_square_popup(municipality_id: Optional[int] = None) -> float:
    """Calculate capacity of renewables per km² (either for municipality or for whole region).

    Parameters
    ----------
    municipality_id: Optional[int]
        If given, capacity of renewables per km² for given municipality are calculated. If not, for whole region.

    Returns
    -------
    float
        Sum of installed renewables
    """
    value = capacity_popup(municipality_id)
    capacity = calculate_square_for_value(value, municipality_id)
    return capacity


# pylint: disable=W0613
def capacity_square_chart(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
    """Get chart for capacity of renewables per km².

    Parameters
    ----------
    chart: dict
        Default chart options for capacity of renewables per km² from JSON
    municipality_id: int
        Related municipality

    Returns
    -------
    dict
        Chart data to use in JS
    """
    chart["series"][0]["data"] = [{"key": 2023, "value": 2}, {"key": 2045, "value": 3}, {"key": 2050, "value": 4}]
    return chart


def capacity_square_choropleth() -> dict[int, int]:
    """Calculate capacity of renewables per km² per municipality.

    Returns
    -------
    dict[int, int]
        Capacity per km² per municipality
    """
    capacity = capacity_choropleth()
    for key, value in capacity.items():
        capacity[key] = calculate_square_for_value(value, key)
    return capacity


LOOKUPS: dict[str, LookupFunctions] = {
    "capacity": LookupFunctions(capacity_popup, capacity_chart, capacity_choropleth),
    "capacity_square": LookupFunctions(capacity_square_popup, capacity_square_chart, capacity_square_choropleth),
    "population": LookupFunctions(
        partial(models.Population.quantity, year=2022),
        models.Population.population_history,
        models.Population.choropleth,
    ),
    "population_density": LookupFunctions(
        models.Population.density_in_2022, models.Population.density_history, models.Population.denisty_choropleth
    ),
    "wind_turbines": LookupFunctions(
        models.WindTurbine.number_per_mun, models.WindTurbine.chart, models.WindTurbine.choropleth
    ),
    "wind_turbines_square": LookupFunctions(
        models.WindTurbine.number_per_square, models.WindTurbine.square_chart, models.WindTurbine.square_choropleth
    ),
}
