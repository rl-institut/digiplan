"""Module for calculations used for choropleths or charts."""

from typing import Optional

from django.db.models import Sum
from oemof.tabular.postprocessing import calculations, core

from digiplan.map import models


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


electricity_demand = core.ParametrizedCalculation(
    calculations.AggregatedFlows,
    {
        "from_nodes": ["ABW-electricity"],
    },
)

heat_demand = core.ParametrizedCalculation(
    calculations.AggregatedFlows,
    {
        "to_nodes": [
            "ABW-heat_decentral-demand_hh",
            "ABW-heat_decentral-demand_cts",
            "ABW-heat_decentral-demand_ind",
            "ABW-heat_central-demand_hh",
            "ABW-heat_central-demand_cts",
            "ABW-heat_central-demand_ind",
        ],
    },
)

electricity_production = core.ParametrizedCalculation(
    calculations.AggregatedFlows,
    {
        "to_nodes": [
            "ABW-electricity",
        ],
    },
)

heat_production = core.ParametrizedCalculation(
    calculations.AggregatedFlows,
    {
        "to_nodes": [
            "ABW-heat_decentral",
            "ABW-heat_central",
        ],
    },
)
