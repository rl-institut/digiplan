"""Module for calculations used for choropleths or charts."""

import pandas as pd
from django.db.models import Sum
from django_oemof.results import get_results
from oemof.tabular.postprocessing import calculations, core

from digiplan.map import config, models


def calculate_square_for_value(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate values related to municipality areas.

    Parameters
    ----------
    df: pd.DataFrame
        Index holds municipality IDs, columns hold random entries

    Returns
    -------
    pd.DataFrame
        Each value is multiplied by related municipality share
    """
    is_series = False
    if isinstance(df, pd.Series):
        is_series = True
        df = pd.DataFrame(df)  # noqa: PD901
    areas = (
        pd.DataFrame.from_records(models.Municipality.objects.all().values("id", "area")).set_index("id").sort_index()
    )
    areas = areas / areas.sum()
    result = df.sort_index() * areas.to_numpy()
    if is_series:
        return result.iloc[:, 0]
    return result


def capacities_per_municipality() -> pd.DataFrame:
    """
    Calculate capacity of renewables per municipality.

    Returns
    -------
    pd.DataFrame
        Capacity per municipality (index) and technology (column)
    """
    capacities = []
    for technology in (
        models.WindTurbine,
        models.PVroof,
        models.PVground,
        models.Hydro,
        models.Biomass,
        models.Storage,
    ):
        res_capacity = pd.DataFrame.from_records(
            technology.objects.values("mun_id").annotate(capacity=Sum("capacity_net")).values("mun_id", "capacity"),
        ).set_index("mun_id")
        res_capacity.columns = [technology._meta.verbose_name]  # noqa: SLF001
        capacities.append(res_capacity)
    return pd.concat(capacities, axis=1).fillna(0.0)


def detailed_overview(simulation_id: int) -> pd.DataFrame:  # noqa: ARG001
    """
    Calculate data for detailed overview chart from simulation ID.

    Parameters
    ----------
    simulation_id: int
        Simulation ID to calculate results from

    Returns
    -------
    pandas.DataFrame
        holding data for detailed overview chart
    """
    # TODO(Hendrik): Calculate real data
    # https://github.com/rl-institut-private/digiplan/issues/164
    return pd.DataFrame(
        data={"production": [300, 200, 200, 150, 520, 0], "consumption": [0, 0, 0, 0, 0, 1300]},
        index=["wind", "pv_roof", "pv_ground", "biomass", "fossil", "consumption"],
    )


def electricity_from_from_biomass(simulation_id: int) -> pd.Series:
    """
    Calculate electricity from biomass.

    Biomass share to electricity comes from following parts:
    - biomass is turned into biogas
    - biogas powers central and decentral BPCHP which outputs to electricity bus
    - wood powers central and decentral EXTCHP which outputs to electricity bus

    - biogas is further upgraded into methane
    - methane powers following components which all output to electricity bus:
      - BPCHP (central/decentral)
      - EXTCHP (central/decentral)
      - gas turbine

    Regarding the power delivered by methane, we have to distinguish between methane from import and methane from
    upgraded biomass. This is done, by calculating the share of both and multiplying output respectively.

    Returns
    -------
    pd.Series
        containing one entry for electric energy powered by biomass
    """
    results = get_results(
        simulation_id,
        {
            "electricity_production": electricity_production,
            "methane_production": methane_production,
        },
    )
    biomass = results["electricity_production"][
        results["electricity_production"]
        .index.get_level_values(0)
        .isin(
            [
                "ABW-wood-extchp_central",
                "ABW-wood-extchp_decentral",
                "ABW-biogas-bpchp_central",
                "ABW-biogas-bpchp_decentral",
            ],
        )
    ]
    methane_total = results["methane_production"].sum()
    methane_biomass_share = results["methane_production"].loc[["ABW-biogas-biogas_upgrading_plant"]] / methane_total
    electricity_from_methane = (
        results["electricity_production"][
            results["electricity_production"]
            .index.get_level_values(0)
            .isin(
                [
                    "ABW-ch4-gt",
                    "ABW-ch4-extchp_central",
                    "ABW-ch4-extchp_decentral",
                    "ABW-ch4-bpchp_central",
                    "ABW-ch4-bpchp_decentral",
                ],
            )
        ]
        * methane_biomass_share.sum()
    )
    biomass = pd.concat([biomass, electricity_from_methane])
    return biomass.sum()


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
    renewables = results["electricity_production"][
        results["electricity_production"].index.get_level_values(0).isin(config.SIMULATION_RENEWABLES)
    ]
    renewables.index = renewables.index.get_level_values(0)
    renewables = pd.concat([renewables, pd.Series(electricity_from_from_biomass(simulation_id), index=["ABW-biomass"])])

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


def heat_overview(simulation_id: int) -> pd.Series:
    """
    Return data for heat overview chart.

    Parameters
    ----------
    simulation_id: int
        Simulation ID to get results from

    Returns
    -------
    pd.Series
        containing heat demand for all sectors (hh, cts, ind)
    """
    results = get_results(
        simulation_id,
        {
            "heat_demand": heat_demand,
        },
    )
    demand = results["heat_demand"]
    demand.index = demand.index.map(lambda ind: f"heat-demand-{ind[1].split('_')[2]}")
    return demand.groupby(level=0).sum()


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

methane_production = core.ParametrizedCalculation(
    calculations.AggregatedFlows,
    {
        "to_nodes": [
            "ABW-ch4",
        ],
    },
)
