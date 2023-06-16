"""Module for calculations used for choropleths or charts."""

from typing import Optional

import pandas as pd
from django.db.models import Sum
from django_oemof.results import get_results
from oemof.tabular.postprocessing import calculations, core

from digiplan.map import config, models


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


def electricity_heat_demand(simulation_id: int) -> pd.Series:
    """
    Return electricity demand for heat demand supply.

    Parameters
    ----------
    simulation_id: int
        Simulation ID to get results from

    Returns
    -------
    pd.Series
        containing electricity demand of heating sector
    """
    results = get_results(
        simulation_id,
        {
            "electricity_demand": electricity_demand,
            "heat_demand": heat_demand,
        },
    )

    heat_central_electricity_production = (
        results["electricity_demand"].loc[:, ["ABW-electricity-heatpump_central"]].iloc[0]
    )
    heat_demand_central = results["heat_demand"][results["heat_demand"].index.get_level_values(0) == "ABW-heat_central"]
    heat_demand_central.index = heat_demand_central.index.get_level_values(1)
    electricity_for_heat_central = heat_demand_central / heat_demand_central.sum() * heat_central_electricity_production
    electricity_for_heat_central.index = electricity_for_heat_central.index.map(
        lambda x: f"electricity_heat_demand_{x.split('_')[2]}",
    )

    heat_decentral_electricity_production = (
        results["electricity_demand"].loc[:, ["ABW-electricity-heatpump_decentral"]].iloc[0]
    )
    heat_demand_decentral = results["heat_demand"][
        results["heat_demand"].index.get_level_values(0) == "ABW-heat_decentral"
    ]
    heat_demand_decentral.index = heat_demand_decentral.index.get_level_values(1)
    electricity_for_heat_decentral = (
        heat_demand_decentral / heat_demand_decentral.sum() * heat_decentral_electricity_production
    )
    electricity_for_heat_decentral.index = electricity_for_heat_decentral.index.map(
        lambda x: f"electricity_heat_demand_{x.split('_')[2]}",
    )

    electricity_for_heat_sum = electricity_for_heat_central + electricity_for_heat_decentral
    return electricity_for_heat_sum


def electricity_overview(simulation_id: int) -> pd.Series:
    """
    Return data for electricity overview chart.

    Parameters
    ----------
    simulation_id: int
        Simulation ID to get results from

    Returns
    -------
    pd.Series
        containing electricity productions and demands (including heat sector demand for electricity)
    """
    results = get_results(
        simulation_id,
        {
            "electricity_demand": electricity_demand,
            "electricity_production": electricity_production,
        },
    )
    # TODO(Hendrik): How to determine biomass electricity production?  # noqa: TD003
    renewables = results["electricity_production"][
        results["electricity_production"].index.get_level_values(0).isin(config.SIMULATION_RENEWABLES)
    ]
    renewables.index = renewables.index.get_level_values(0)

    electricity_import = results["electricity_production"].loc[["ABW-electricity-import"]]
    electricity_import.index = electricity_import.index.get_level_values(0)
    electricity_export = results["electricity_demand"].loc[:, ["ABW-electricity-export"]]
    electricity_export.index = electricity_export.index.get_level_values(1)

    demand = results["electricity_demand"][
        results["electricity_demand"].index.get_level_values(1).isin(config.SIMULATION_DEMANDS)
    ]
    demand.index = demand.index.get_level_values(1)

    electricity_heat_production_result = electricity_heat_demand(simulation_id)

    return pd.concat([renewables, demand, electricity_heat_production_result])


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
