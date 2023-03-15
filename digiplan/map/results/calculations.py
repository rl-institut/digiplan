"""Module for calculations used for choropleths or charts."""

import json
import pathlib
from collections import namedtuple
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
    chart = LOOKUPS[lookup].chart_fct(chart, municipality_id)
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
    data["data"]["municipality_value"] = LOOKUPS[lookup].data_fct(municipality_id)
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


def get_data_for_capacity(municipality_id: Optional[int] = None) -> float:
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
    values = get_capacity()

    if municipality_id is not None:
        capacity = values[municipality_id]
    else:
        for _key, value in values.items():
            capacity += value
    return capacity


# pylint: disable=W0613
def get_chart_for_capacity(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
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


def get_capacity() -> dict[int, int]:
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


def get_data_for_population(municipality_id: Optional[int] = None) -> int:
    """Calculate population in 2022 (either for municipality or for whole region).

    Parameters
    ----------
    municipality_id: Optional[int]
        If given, population for given municipality are calculated. If not, for whole region.

    Returns
    -------
    int
        Value of population
    """
    values = get_population()
    population = 0.0

    if municipality_id is not None:
        population = values[municipality_id]
    else:
        for index in values:
            population += values[index]
    return population


def get_chart_for_population(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
    """Get chart for population per municipality in different years.

    Parameters
    ----------
    chart: dict
        Default chart options for population from JSON
    municipality_id: int
        Related municipality

    Returns
    -------
    dict
        Chart data to use in JS
    """
    chart["series"][0]["data"] = [{"key": 2023, "value": 2}, {"key": 2045, "value": 3}, {"key": 2050, "value": 4}]
    return chart


def get_population() -> dict[int, int]:
    """Calculate population per municipality.

    Returns
    -------
    dict[int, int]
        Population per municipality
    """
    return {row.municipality_id: row.value for row in models.Population.objects.filter(year=2022)}


def get_data_for_population_square(municipality_id: Optional[int] = None) -> float:
    """Calculate population in 2022 per km² (either for municipality or for whole region).

    Parameters
    ----------
    municipality_id: Optional[int]
        If given, population per km² for given municipality are calculated. If not, for whole region.

    Returns
    -------
    float
        Value of population
    """
    population = get_data_for_population(municipality_id)

    density = calculate_square_for_value(population, municipality_id)
    return density


def get_chart_for_population_square(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
    """Get chart for population density for the given municipality in different years.

    Parameters
    ----------
    chart: dict
        Default chart options for population density from JSON
    municipality_id: int
        Related municipality

    Returns
    -------
    dict
        Chart data to use in JS
    """
    chart["series"][0]["data"] = [{"key": 2023, "value": 2}, {"key": 2045, "value": 3}, {"key": 2050, "value": 4}]
    return chart


def get_population_square() -> dict[int, int]:
    """Calculate population per municipality.

    Returns
    -------
    dict[int, int]
        Population per municipality
    """
    density = get_population()
    for index in density:
        density[index] = calculate_square_for_value(density[index], index)
    return density


def get_data_for_windturbines(municipality_id: Optional[int] = None) -> float:
    """Calculate number of windturbines (either for municipality or for whole region).

    Parameters
    ----------
    municipality_id: Optional[int]
        If given, number of windturbines for given municipality are calculated. If not, for whole region.

    Returns
    -------
    float
        Sum of windturbines
    """
    windturbines = 0.0
    if municipality_id is not None:
        res_windturbine = models.WindTurbine.objects.filter(mun_id__exact=municipality_id).aggregate(Sum("unit_count"))[
            "unit_count__sum"
        ]
    else:
        res_windturbine = models.WindTurbine.objects.aggregate(Sum("unit_count"))["unit_count__sum"]
    if res_windturbine:
        windturbines += res_windturbine
    return windturbines


def get_chart_for_wind_turbines(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
    """Get chart for wind turbines.

    Parameters
    ----------
    chart: dict
        Default chart options for wind turbines from JSON
    municipality_id: int
        Related municipality

    Returns
    -------
    dict
        Chart data to use in JS
    """
    chart["series"][0]["data"] = [{"key": 2023, "value": 2}, {"key": 2045, "value": 3}, {"key": 2050, "value": 4}]
    return chart


def get_data_for_windturbines_square(municipality_id: Optional[int] = None) -> float:
    """Calculate number of windturbines per km² (either for municipality or for whole region).

    Parameters
    ----------
    municipality_id: Optional[int]
        If given, number of windturbines per km² for given municipality are calculated. If not, for whole region.

    Returns
    -------
    float
        Sum of windturbines per km²
    """
    windturbines = get_data_for_windturbines(municipality_id)

    windturbines_square = calculate_square_for_value(windturbines, municipality_id)
    return windturbines_square


def get_chart_for_wind_turbines_square(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
    """Get chart for wind turbines per km².

    Parameters
    ----------
    chart: dict
        Default chart options for wind turbines from JSON
    municipality_id: int
        Related municipality

    Returns
    -------
    dict
        Chart data to use in JS
    """
    chart["series"][0]["data"] = [{"key": 2023, "value": 2}, {"key": 2045, "value": 3}, {"key": 2050, "value": 4}]
    return chart


LOOKUPS: dict[str, LookupFunctions] = {
    "capacity": LookupFunctions(get_data_for_capacity, get_chart_for_capacity, get_capacity),
    "population": LookupFunctions(get_data_for_population, get_chart_for_population, get_population),
    "population_density": LookupFunctions(
        get_data_for_population_square, get_chart_for_population_square, get_population_square
    ),
    "wind_turbines": LookupFunctions(get_data_for_windturbines, get_chart_for_wind_turbines, None),
    "wind_turbines_square": LookupFunctions(get_data_for_windturbines_square, get_chart_for_wind_turbines_square, None),
}
