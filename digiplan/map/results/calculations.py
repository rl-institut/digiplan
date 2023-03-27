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


def population_popup(municipality_id: Optional[int] = None) -> int:
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
    values = population_choropleth()
    population = 0.0

    if municipality_id is not None:
        population = values[municipality_id]
    else:
        for index in values:
            population += values[index]
    return population


def population_chart(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
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
    values = models.Population.objects.filter(municipality_id=municipality_id).values_list("year", "value")
    data_list = []
    for _mun, value in enumerate(values):
        data_list.append({"key": value[0], "value": value[1]})

    chart["series"][0]["data"] = data_list
    return chart


def population_choropleth() -> dict[int, int]:
    """Calculate population per municipality.

    Returns
    -------
    dict[int, int]
        Population per municipality
    """
    return {row.municipality_id: row.value for row in models.Population.objects.filter(year=2022)}


def population_square_popup(municipality_id: Optional[int] = None) -> float:
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
    population = population_popup(municipality_id)

    density = calculate_square_for_value(population, municipality_id)
    return density


def population_square_chart(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
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


def population_square_choropleth() -> dict[int, int]:
    """Calculate population per municipality.

    Returns
    -------
    dict[int, int]
        Population per municipality
    """
    density = population_choropleth()
    for index in density:
        density[index] = calculate_square_for_value(density[index], index)
    return density


def windturbines_popup(municipality_id: Optional[int] = None) -> int:
    """Calculate number of windturbines (either for municipality or for whole region).

    Parameters
    ----------
    municipality_id: Optional[int]
        If given, number of windturbines for given municipality are calculated. If not, for whole region.

    Returns
    -------
    int
        Sum of windturbines
    """
    windturbines = 0
    if municipality_id is not None:
        res_windturbine = models.WindTurbine.objects.filter(mun_id__exact=municipality_id).aggregate(Sum("unit_count"))[
            "unit_count__sum"
        ]
    else:
        res_windturbine = models.WindTurbine.objects.aggregate(Sum("unit_count"))["unit_count__sum"]
    if res_windturbine:
        windturbines += res_windturbine
    return windturbines


def windturbines_chart(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
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


def windturbines_choropleth() -> dict[int, int]:
    """Calculate number of wind turbines per municipality.

    Returns
    -------
    dict[int, int]
        wind turbines per municipality
    """

    windturbines = {}
    municipalities = models.Municipality.objects.all()

    for mun in municipalities:
        res_windturbine = models.WindTurbine.objects.filter(mun_id__exact=mun.id).aggregate(Sum("unit_count"))[
            "unit_count__sum"
        ]
        if res_windturbine is None:
            res_windturbine = 0
        windturbines[mun.id] = res_windturbine
    return windturbines


def windturbines_square_popup(municipality_id: Optional[int] = None) -> float:
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
    windturbines = windturbines_popup(municipality_id)

    windturbines_square = calculate_square_for_value(windturbines, municipality_id)
    return windturbines_square


def windturbines_square_chart(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
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


def windturbines_square_choropleth() -> dict[int, int]:
    """Calculate windturbines per km² per municipality.

    Returns
    -------
    dict[int, int]
        windturbines per km² per municipality
    """
    windtubines = windturbines_choropleth()
    for index in windtubines:
        windtubines[index] = calculate_square_for_value(windtubines[index], index)
    return windtubines


LOOKUPS: dict[str, LookupFunctions] = {
    "capacity": LookupFunctions(capacity_popup, capacity_chart, capacity_choropleth),
    "capacity_square": LookupFunctions(capacity_square_popup, capacity_square_chart, capacity_square_choropleth),
    "population": LookupFunctions(population_popup, population_chart, population_choropleth),
    "population_density": LookupFunctions(
        population_square_popup, population_square_chart, population_square_choropleth
    ),
    "wind_turbines": LookupFunctions(windturbines_popup, windturbines_chart, windturbines_choropleth),
    "wind_turbines_square": LookupFunctions(
        windturbines_square_popup, windturbines_square_chart, windturbines_square_choropleth
    ),
}
