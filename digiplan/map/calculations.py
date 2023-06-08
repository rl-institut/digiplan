"""Module for calculations used for choropleths or charts."""

import json
import pathlib
from collections import namedtuple
from functools import partial
from typing import Optional

from django.db.models import Sum
from oemof.tabular.postprocessing import calculations, core

from digiplan.map import config, models

LookupFunctions = namedtuple("PopupData", ("data_fct", "chart_fct", "choropleth_fct"))


def create_choropleth_data(lookup: str) -> dict:
    """
    Create data for every municipality for given lookup.

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


def create_data(lookup: str, municipality_id: int, map_state: dict) -> dict:  # noqa: ARG001
    """
    Create data for given lookup.

    Parameters
    ----------
    lookup: str
        Looks up related data function in LOOKUPS.
    municipality_id: int
        Used to calculate data related to given municipality.
    map_state: dict
        Additional information on current map state

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
    data["data"]["municipality_value"] = LOOKUPS[lookup].data_fct(mun_id=municipality_id)
    data["municipality"] = models.Municipality.objects.get(pk=municipality_id)

    return data


def calculate_square_for_value(value: int, municipality_id: Optional[int]) -> float:
    """
    Calculate value related to municipality area.

    Parameters
    ----------
    value: int
        Value to calculate
    municipality_id: Optional[int]
        ID of municipality to get area from
        If not given, value in relation to area of whole region is calculated.

    Returns
    -------
    float
        Value per square meter
    """
    area = 0.0
    if municipality_id is not None:
        area = models.Municipality.objects.get(pk=municipality_id).area
    else:
        for mun in models.Municipality.objects.all():
            area += models.Municipality.objects.get(pk=mun.id).area
    if area != 0.0:  # noqa: PLR2004
        return value / area
    return value


def capacity_popup(mun_id: Optional[int] = None) -> float:
    """
    Calculate capacity of renewables (either for municipality or for whole region).

    Parameters
    ----------
    mun_id: Optional[int]
        If given, capacity of renewables for given municipality are calculated. If not, for whole region.

    Returns
    -------
    float
        Sum of installed renewables
    """
    capacity = 0.0
    values = capacity_choropleth()

    if mun_id is not None:
        capacity = values[mun_id]
    else:
        for _key, value in values.items():
            capacity += value
    return capacity


# pylint: disable=W0613
def capacity_chart(municipality_id: int) -> dict:  # noqa: ARG001
    """
    Get chart for capacity of renewables.

    Parameters
    ----------
    municipality_id: int
        Related municipality

    Returns
    -------
    dict
        Chart data to use in JS
    """
    return [(2023, 2), (2046, 3), (2050, 4)]


def capacity_choropleth() -> dict[int, int]:
    """
    Calculate capacity of renewables per municipality.

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


def capacity_square_popup(mun_id: Optional[int] = None) -> float:
    """
    Calculate capacity of renewables per km² (either for municipality or for whole region).

    Parameters
    ----------
    mun_id: Optional[int]
        If given, capacity of renewables per km² for given municipality are calculated. If not, for whole region.

    Returns
    -------
    float
        Sum of installed renewables
    """
    value = capacity_popup(mun_id)
    return calculate_square_for_value(value, mun_id)


# pylint: disable=W0613
def capacity_square_chart(municipality_id: int) -> dict:  # noqa: ARG001
    """
    Get chart for capacity of renewables per km².

    Parameters
    ----------
    municipality_id: int
        Related municipality

    Returns
    -------
    dict
        Chart data to use in JS
    """
    return [(2023, 2), (2046, 3), (2050, 4)]


def capacity_square_choropleth() -> dict[int, int]:
    """
    Calculate capacity of renewables per km² per municipality.

    Returns
    -------
    dict[int, int]
        Capacity per km² per municipality
    """
    capacity = capacity_choropleth()
    for key, value in capacity.items():
        capacity[key] = calculate_square_for_value(value, key)
    return capacity


electric_demand = core.ParametrizedCalculation(
    calculations.AggregatedFlows,
    {
        "to_nodes": [
            "ABW-ch4-demand",
            "ABW-electricity-demand",
            "ABW-heat_central-demand",
            "ABW-heat_decentral-demand",
            "ABW-lignite-demand",
            "ABW-wood-demand",
        ],
    },
)

renewable_electricity_production = core.ParametrizedCalculation(
    calculations.AggregatedFlows,
    {
        "from_nodes": [
            "ABW-solar-pv_ground",
        ],
    },
)


LOOKUPS: dict[str, LookupFunctions] = {
    "capacity": LookupFunctions(capacity_popup, capacity_chart, capacity_choropleth),
    "capacity_square": LookupFunctions(capacity_square_popup, capacity_square_chart, capacity_square_choropleth),
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
    "renewable_electricity_production": LookupFunctions(
        models.WindTurbine.quantity_per_square,
        models.WindTurbine.wind_turbines_per_area_history,
        models.WindTurbine.quantity_per_mun_and_area,
    ),
}