"""Module for calculations used for choropleths or charts."""

from typing import Optional

import pandas as pd
from django.conf import settings
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django_oemof.models import Simulation
from django_oemof.results import get_results
from oemof.tabular.postprocessing import calculations, core, helper

from digiplan.map import config, datapackage, models

# TODO (Hendrik): Read wind turbine capacity from datapackage
# https://github.com/rl-institut-private/digiplan/issues/314
DEFAULT_WIND_TURBINE_CAPACITY = 1.5  # MW


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
    result = df / areas.sum().sum() if len(df) == 1 else df.sort_index() / areas.to_numpy()
    if is_series:
        return result.iloc[:, 0]
    return result


def value_per_municipality(series: pd.Series) -> pd.DataFrame:
    """Shares values across areas (dummy function)."""
    data = pd.concat([series] * 20, axis=1).transpose()
    data.index = range(20)
    areas = (
        pd.DataFrame.from_records(models.Municipality.objects.all().values("id", "area")).set_index("id").sort_index()
    )
    result = data.sort_index() / areas.to_numpy()
    return result / areas.sum().sum()


def calculate_capita_for_value(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate values related to population. If only one region is given, whole region is assumed.

    Parameters
    ----------
    df: pd.DataFrame
        Index holds municipality IDs, columns hold random entries

    Returns
    -------
    pd.DataFrame
        Each value is multiplied by related municipality population share
    """
    is_series = False
    if isinstance(df, pd.Series):
        is_series = True
        df = pd.DataFrame(df)  # noqa: PD901

    population = (
        pd.DataFrame.from_records(models.Population.objects.filter(year=2022).values("id", "value"))
        .set_index("id")
        .sort_index()
    )
    result = df / population.sum().sum() if len(df) == 1 else df.sort_index() / population.to_numpy()
    if is_series:
        return result.iloc[:, 0]
    return result


def employment_per_municipality() -> pd.DataFrame:
    """Return employees per municipality."""
    return datapackage.get_employment()["employees_total"]


def companies_per_municipality() -> pd.DataFrame:
    """Return companies per municipality."""
    return datapackage.get_employment()["companies_total"]


def batteries_per_municipality() -> pd.DataFrame:
    """Return battery count per municipality."""
    return datapackage.get_batteries()["count"]


def battery_capacities_per_municipality() -> pd.DataFrame:
    """Return battery capacity per municipality."""
    return datapackage.get_batteries()["storage_capacity"]


def capacities_per_municipality() -> pd.DataFrame:
    """
    Calculate capacity of renewables per municipality in MW.

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
    return pd.concat(capacities, axis=1).fillna(0.0) * 1e-3


def capacities_per_municipality_2045(simulation_id: int) -> pd.DataFrame:
    """Calculate capacities from 2045 scenario per municipality."""
    results = get_results(
        simulation_id,
        {
            "capacities": Capacities,
        },
    )
    renewables = results["capacities"][
        results["capacities"].index.get_level_values(0).isin(config.SIMULATION_RENEWABLES)
    ]
    renewables.index = ["hydro", "pv_ground", "pv_roof", "wind"]
    renewables = renewables.reindex(["wind", "pv_roof", "pv_ground", "hydro"])

    parameters = Simulation.objects.get(pk=simulation_id).parameters
    renewables = renewables * calculate_potential_shares(parameters)
    renewables["bioenergy"] = 0.0
    renewables["st"] = 0.0
    return renewables


def energies_per_municipality() -> pd.DataFrame:
    """
    Calculate energy of renewables per municipality in GWh.

    Returns
    -------
    pd.DataFrame
        Energy per municipality (index) and technology (column)
    """
    capacities = capacities_per_municipality()
    full_load_hours = datapackage.get_full_load_hours(year=2022)
    full_load_hours = full_load_hours.reindex(index=["wind", "pv_roof", "pv_ground", "ror", "bioenergy", "st"])
    return capacities * full_load_hours.values / 1e3


def energies_per_municipality_2045(simulation_id: int) -> pd.DataFrame:
    """Calculate energies from 2045 scenario per municipality."""
    results = get_results(
        simulation_id,
        {
            "electricity_production": electricity_production,
        },
    )
    renewables = results["electricity_production"][
        results["electricity_production"].index.get_level_values(0).isin(config.SIMULATION_RENEWABLES)
    ]
    renewables.index = ["hydro", "pv_ground", "pv_roof", "wind"]
    renewables = renewables.reindex(["wind", "pv_roof", "pv_ground", "hydro"])

    parameters = Simulation.objects.get(pk=simulation_id).parameters
    renewables = renewables * calculate_potential_shares(parameters)
    renewables["bioenergy"] = 0.0
    renewables["st"] = 0.0
    return renewables


def energy_shares_per_municipality() -> pd.DataFrame:
    """
    Calculate energy shares of renewables from electric demand per municipality.

    Returns
    -------
    pd.DataFrame
        Energy share per municipality (index) and technology (column)
    """
    energies = energies_per_municipality()
    demands = datapackage.get_power_demand()
    total_demand = pd.concat([d["2022"] for d in demands.values()], axis=1).sum(axis=1)
    total_demand_share = total_demand / total_demand.sum()
    energies = energies.reindex(range(20))
    return energies.mul(total_demand_share, axis=0)


def electricity_demand_per_municipality(year: int = 2022) -> pd.DataFrame:
    """
    Calculate electricity demand per sector per municipality in GWh.

    Returns
    -------
    pd.DataFrame
        Electricity demand per municipality (index) and sector (column)
    """
    demands_raw = datapackage.get_power_demand()
    demands_per_sector = pd.concat([demand[str(year)] for demand in demands_raw.values()], axis=1)
    demands_per_sector.columns = [
        _("Electricity Household Demand"),
        _("Electricity CTS Demand"),
        _("Electricity Industry Demand"),
    ]
    return demands_per_sector * 1e-3


def electricity_demand_per_municipality_2045(simulation_id: int) -> pd.DataFrame:
    """
    Calculate electricity demand per sector per municipality in GWh in 2045.

    Returns
    -------
    pd.DataFrame
        Electricity demand per municipality (index) and sector (column)
    """
    results = get_results(
        simulation_id,
        {
            "electricity_demand": electricity_demand,
        },
    )
    demand = results["electricity_demand"][
        results["electricity_demand"].index.get_level_values(1).isin(config.SIMULATION_DEMANDS)
    ]
    demand = demand.droplevel([0, 2])
    demands_per_sector = datapackage.get_power_demand()
    mappings = {
        "hh": "ABW-electricity-demand_hh",
        "cts": "ABW-electricity-demand_cts",
        "ind": "ABW-electricity-demand_ind",
    }
    demand = demand.reindex(mappings.values())
    sector_shares = pd.DataFrame(
        {sector: demands_per_sector[sector]["2045"] / demands_per_sector[sector]["2045"].sum() for sector in mappings},
    )
    demand = sector_shares * demand.values
    demand.columns = demand.columns.map(lambda column: config.SIMULATION_DEMANDS[mappings[column]])
    demand = demand * 1e-3
    return demand


def heat_demand_per_municipality() -> pd.DataFrame:
    """
    Calculate heat demand per sector per municipality in GWh.

    Returns
    -------
    pd.DataFrame
        Heat demand per municipality (index) and sector (column)
    """
    demands_raw = datapackage.get_summed_heat_demand_per_municipality()
    demands_per_sector = pd.concat(
        [distributions["cen"]["2022"] + distributions["dec"]["2022"] for distributions in demands_raw.values()],
        axis=1,
    )
    demands_per_sector.columns = [
        _("Electricity Household Demand"),
        _("Electricity CTS Demand"),
        _("Electricity Industry Demand"),
    ]
    return demands_per_sector * 1e-3


def heat_demand_per_municipality_2045(simulation_id: int) -> pd.DataFrame:
    """
    Calculate heat demand per sector per municipality in GWh in 2045.

    Returns
    -------
    pd.DataFrame
        Heat demand per municipality (index) and sector (column)
    """
    results = get_results(
        simulation_id,
        {
            "heat_demand": heat_demand,
        },
    )
    demand = results["heat_demand"]
    demand.index = demand.index.map(lambda ind: f"heat-demand-{ind[1].split('_')[2]}")
    demand = demand.groupby(level=0).sum()
    demands_per_sector = datapackage.get_heat_demand()
    mappings = {
        "hh": "heat-demand-hh",
        "cts": "heat-demand-cts",
        "ind": "heat-demand-ind",
    }
    demand = demand.reindex(mappings.values())
    sector_shares = pd.DataFrame(
        {sector: demands_per_sector[sector]["2045"] / demands_per_sector[sector]["2045"].sum() for sector in mappings},
    )
    demand = sector_shares * demand.values
    demand.columns = demand.columns.map(lambda column: config.SIMULATION_DEMANDS[mappings[column]])
    demand = demand * 1e-3
    return demand


def ghg_reduction(simulation_id: int) -> pd.Series:
    """
    Calculate data for GHG reduction chart from simulation ID.

    Parameters
    ----------
    simulation_id: int
        Simulation ID to calculate results from

    Returns
    -------
    pandas.Series
        holding data for GHG reduction chart
    """
    renewables = renewable_electricity_production(simulation_id).sum()

    results = get_results(
        simulation_id,
        {
            "electricity_production": electricity_production,
        },
    )
    electricity_import = results["electricity_production"].loc[["ABW-electricity-import"]]
    electricity_import.index = electricity_import.index.get_level_values(0)
    electricity_import["ABW-renewables"] = renewables
    return electricity_import * 1e-3


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


def wind_turbines_per_municipality_2045(simulation_id: int) -> pd.DataFrame:
    """Calculate number of wind turbines from 2045 scenario per municipality."""
    capacities = capacities_per_municipality_2045(simulation_id)
    return capacities["wind"] / DEFAULT_WIND_TURBINE_CAPACITY


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


def calculate_potential_shares(parameters: dict) -> pd.DataFrame:
    """Calculate potential shares depending on user settings."""
    # DISAGGREGATION
    # Wind
    wind_areas = pd.read_csv(
        settings.DIGIPIPE_DIR.path("scalars").path("potentialarea_wind_area_stats_muns.csv"),
        index_col=0,
    )
    if parameters["s_w_3"]:
        wind_area_per_mun = wind_areas["stp_2018_vreg"]
    elif parameters["s_w_4_1"]:
        wind_area_per_mun = wind_areas["stp_2027_vr"]
    elif parameters["s_w_4_2"]:
        wind_area_per_mun = wind_areas["stp_2027_repowering"]
    elif parameters["s_w_5"]:
        wind_area_per_mun = (
            wind_areas["stp_2027_search_area_open_area"] * parameters["s_w_5_1"] / 100
            + wind_areas["stp_2027_search_area_forest_area"] * parameters["s_w_5_2"] / 100
        )
    else:
        msg = "No wind switch set"
        raise KeyError(msg)
    wind_share_per_mun = wind_area_per_mun / wind_area_per_mun.sum()

    # PV ground
    pv_ground_areas = pd.read_csv(
        settings.DIGIPIPE_DIR.path("scalars").path("potentialarea_pv_ground_area_stats_muns.csv", index_col=0),
    )
    pv_ground_area_per_mun = (
        pv_ground_areas["agriculture_lfa-off_region"] * parameters["s_pv_ff_3"] / 100
        + pv_ground_areas["road_railway_region"] * parameters["s_pv_ff_4"] / 100
    )
    pv_ground_share_per_mun = pv_ground_area_per_mun / pv_ground_area_per_mun.sum()

    # PV roof
    pv_roof_areas = pd.read_csv(
        settings.DIGIPIPE_DIR.path("scalars").path("potentialarea_pv_roof_area_stats_muns.csv"),
        index_col=0,
    )
    pv_roof_area_per_mun = pv_roof_areas["installable_power_total"]
    pv_roof_share_per_mun = pv_roof_area_per_mun / pv_roof_area_per_mun.sum()

    # Hydro
    hydro_areas = pd.read_csv(
        settings.DIGIPIPE_DIR.path("scalars").path("bnetza_mastr_hydro_stats_muns.csv"),
        index_col=0,
    )
    hydro_area_per_mun = hydro_areas["capacity_net"]
    hydro_share_per_mun = hydro_area_per_mun / hydro_area_per_mun.sum()

    shares = pd.concat(
        [wind_share_per_mun, pv_roof_share_per_mun, pv_ground_share_per_mun, hydro_share_per_mun],
        axis=1,
    )
    shares.columns = ["wind", "pv_roof", "pv_ground", "hydro"]
    return shares


def electricity_overview(year: int) -> pd.Series:
    """
    Return static data for electricity overview chart for given year.

    Parameters
    ----------
    year: int
        Year, either 2022 or 2045

    Returns
    -------
    pd.Series
        containing electricity productions and demands (including heat sector demand for electricity)
    """
    demand = electricity_demand_per_municipality(year).sum()
    production = datapackage.get_full_load_hours(year) * datapackage.get_capacities(year)
    production = production[production.notna()] * 1e-3
    return pd.concat([demand, production])


def electricity_overview_from_user(simulation_id: int) -> pd.Series:
    """
    Return user specific data for electricity overview chart.

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
    demand = results["electricity_demand"][
        results["electricity_demand"]
        .index.get_level_values(1)
        .isin([*list(config.SIMULATION_DEMANDS), "ABW-electricity-export"])
    ]
    demand.index = demand.index.get_level_values(1)

    electricity_heat_production_result = electricity_heat_demand(simulation_id)
    demand["ABW-electricity-demand_hh"] += electricity_heat_production_result["electricity_heat_demand_hh"]
    demand["ABW-electricity-demand_cts"] += electricity_heat_production_result["electricity_heat_demand_cts"]
    demand["ABW-electricity-demand_ind"] += electricity_heat_production_result["electricity_heat_demand_ind"]

    renewables = renewable_electricity_production(simulation_id)

    production_import = results["electricity_production"][
        results["electricity_production"].index.get_level_values(0).isin(["ABW-electricity-import"])
    ]
    production_import.index = ["ABW-electricity-import"]

    overview_data = pd.concat([renewables, demand, production_import])
    overview_data = overview_data.reindex(
        (
            "ABW-wind-onshore",
            "ABW-solar-pv_ground",
            "ABW-solar-pv_rooftop",
            "ABW-biomass",
            "ABW-hydro-ror",
            "ABW-electricity-demand_cts",
            "ABW-electricity-demand_hh",
            "ABW-electricity-demand_ind",
            "ABW-electricity-import",
            "ABW-electricity-export",
        ),
    )
    overview_data = overview_data * 1e-3
    return overview_data


def renewable_electricity_production(simulation_id: int) -> pd.Series:
    """Return electricity production from renewables including biomass."""
    results = get_results(
        simulation_id,
        {
            "electricity_production": electricity_production,
        },
    )
    renewables = results["electricity_production"][
        results["electricity_production"].index.get_level_values(0).isin(config.SIMULATION_RENEWABLES)
    ]
    renewables.index = renewables.index.get_level_values(0)
    renewables = pd.concat([renewables, pd.Series(electricity_from_from_biomass(simulation_id), index=["ABW-biomass"])])
    return renewables


def get_regional_independency(simulation_id: int) -> tuple[int, int, int, int]:
    """Return electricity autarky for 2022 and user scenario."""
    # 2022
    demand = datapackage.get_hourly_electricity_demand(2022)
    full_load_hours = datapackage.get_full_load_hours(2022)
    capacities = datapackage.get_capacities(2022)
    technology_mapping = {
        "ABW-wind-onshore": "wind",
        "ABW-solar-pv_ground": "pv_ground",
        "ABW-solar-pv_rooftop": "pv_roof",
        "ABW-hydro-ror": "ror",
    }
    renewables = []
    for technology, mapped_key in technology_mapping.items():
        renewables.append(
            datapackage.get_profile(technology[4:]) * full_load_hours[mapped_key] * capacities[mapped_key],
        )
    renewables_summed_flow = pd.concat(renewables, axis=1).sum(axis=1)
    # summary
    independency_summary_2022 = round(renewables_summed_flow.sum() / demand.sum() * 100)
    # temporal
    independency_temporal_2022 = renewables_summed_flow - demand
    independency_temporal_2022 = round(sum(independency_temporal_2022 > 0) / 8760 * 100)

    # USER
    results = get_results(
        simulation_id,
        {"renewable_flows": renewable_flows, "demand_flows": demand_flows},
    )
    # summary
    independency_summary = round(results["renewable_flows"].sum().sum() / results["demand_flows"].sum().sum() * 100)
    # temporal
    independency_temporal = results["renewable_flows"].sum(axis=1) - results["demand_flows"].sum(axis=1)
    independency_temporal = round(sum(independency_temporal > 0) / 8760 * 100)
    return independency_summary_2022, independency_temporal_2022, independency_summary, independency_temporal


def get_heat_production(distribution: str, year: int) -> dict:
    """Calculate hea production per technology for given distribution and year."""
    heat_demand_per_sector = datapackage.get_heat_demand(distribution=distribution)
    demand = sum(d[str(year)].sum() for d in heat_demand_per_sector.values())
    heat_shares = datapackage.get_heat_capacity_shares(distribution[:3], year=year, include_heatpumps=True)
    return {tech: demand * share for tech, share in heat_shares.items()}


def get_reduction(simulation_id: int) -> tuple[int, int]:
    """Return electricity reduction from renewables and imports."""
    results = get_results(
        simulation_id,
        {"renewables": reduction_from_renewables, "imports": reduction_from_imports},
    )
    reduction = 2425.9
    res_reduction = results["renewables"].sum()
    import_reduction = results["imports"].sum()
    summed_reduction = res_reduction + import_reduction
    return round(import_reduction / summed_reduction * reduction), round(res_reduction / summed_reduction * reduction)


def heat_overview(simulation_id: int, distribution: str) -> dict:
    """
    Return data for heat overview chart.

    Parameters
    ----------
    simulation_id: int
        Simulation ID to get results from
    distribution: str
        central/decentral

    Returns
    -------
    dict
        containing heat demand and production for all sectors (hh, cts, ind) and technologies
    """
    data = {}
    for year in (2022, 2045):
        demand = datapackage.get_heat_demand(distribution=distribution)
        demand = {f"heat-demand-{sector}": demand[str(year)].sum() for sector, demand in demand.items()}
        data[str(year)] = demand
        data[str(year)].update(get_heat_production(distribution, year))

    results = get_results(
        simulation_id,
        {"heat_demand": heat_demand, "heat_production": heat_production},
    )
    # Filter distribution:
    if distribution == "central":
        demand = results["heat_demand"][
            results["heat_demand"].index.get_level_values(0).map(lambda idx: "decentral" not in idx)
        ]
        production = results["heat_production"][
            results["heat_production"]
            .index.get_level_values(0)
            .map(lambda idx: "decentral" not in idx and idx not in ("ABW-wood-oven", "ABW-heat-import"))
        ]
    else:
        demand = results["heat_demand"][
            results["heat_demand"].index.get_level_values(0).map(lambda idx: "decentral" in idx)
        ]
        production = results["heat_production"][
            results["heat_production"]
            .index.get_level_values(0)
            .map(lambda idx: "decentral" in idx or idx in ("ABW-wood-oven", "ABW-heat-import"))
        ]

    # Demand from user scenario:
    demand.index = demand.index.map(lambda ind: f"heat-demand-{ind[1].split('_')[2]}")
    data["user"] = demand.to_dict()
    # Production from user scenario:
    production.index = production.index.map(lambda ind: ind[0][4:].split("_")[0])
    mapping = {
        "biogas-bpchp": "biogas_bpchp",
        "ch4-boiler": "biogas_bpchp",  # As in future all methane comes from biogas
        "ch4-bpchp": "biogas_bpchp",
        "ch4-extchp": "biogas_bpchp",
        "electricity-heatpump": "heat_pump",
        "electricity-pth": "electricity_direct_heating",
        "solar-thermalcollector": "solar_thermal",
        "wood-extchp": "wood_extchp",
        "wood-bpchp": "wood_bpchp",
        "wood-oven": "wood_oven",
    }
    production = production[production.index.map(lambda idx: idx in mapping)]
    production.index = production.index.map(mapping)
    production = production.reset_index().groupby("index").sum().iloc[:, 0]
    data["user"].update(production.to_dict())
    return data


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

reduction_from_renewables = core.ParametrizedCalculation(
    calculations.AggregatedFlows,
    {
        "from_nodes": [
            "ABW-wind-onshore",
            "ABW-pv_rooftop",
            "ABW-pv_ground",
            "ABW-hydro-ror",
            "ABW-solar-thermalcollector_central",
            "ABW-solar-thermalcollector_decentral",
        ],
    },
)

reduction_from_imports = core.ParametrizedCalculation(
    calculations.AggregatedFlows,
    {
        "from_nodes": [
            "ABW-electricity-import",
            "ABW-ch4-import",
            "ABW-wood-shortage",
            "ABW-lignite-shortage",
            "ABW-biomass-shortage",
        ],
    },
)


class Capacities(core.Calculation):
    """Oemof postprocessing calculation to read capacities."""

    name = "capacities"

    def calculate_result(self) -> pd.Series:
        """Read attribute "capacity" from parameters."""
        capacities = helper.filter_by_var_name(self.scalar_params, "capacity")
        try:
            return capacities.unstack(2)["capacity"]  # noqa: PD010
        except KeyError:
            return pd.Series(dtype="object")


class Flows(core.Calculation):
    """Oemof postprocessing calculation to read flows."""

    name = "flows"

    def __init__(
        self,
        calculator: core.Calculator,
        from_nodes: Optional[list[str]] = None,
        to_nodes: Optional[list[str]] = None,
    ) -> None:
        """Init flows."""
        if not from_nodes and not to_nodes:
            msg = "Either from or to nodes must be set"
            raise ValueError(msg)
        self.from_nodes = from_nodes
        self.to_nodes = to_nodes

        super().__init__(calculator)

    def calculate_result(self) -> pd.DataFrame:
        """Read attribute "capacity" from parameters."""
        from_node_flows = pd.DataFrame()
        to_node_flows = pd.DataFrame()
        if self.from_nodes:
            from_node_flows = self.sequences.iloc[:, self.sequences.columns.get_level_values(0).isin(self.from_nodes)]
            from_node_flows.columns = from_node_flows.columns.droplevel([1, 2])
        if self.to_nodes:
            to_node_flows = self.sequences.iloc[:, self.sequences.columns.get_level_values(1).isin(self.to_nodes)]
            to_node_flows.columns = to_node_flows.columns.droplevel([0, 2])
        return pd.concat([from_node_flows, to_node_flows], axis=1)


renewable_flows = core.ParametrizedCalculation(
    Flows,
    {
        "from_nodes": ["ABW-wind-onshore", "ABW-solar-pv_rooftop", "ABW-solar-pv_ground", "ABW-hydro-ror"],
    },
)

demand_flows = core.ParametrizedCalculation(
    Flows,
    {
        "to_nodes": [
            "ABW-electricity-demand_hh",
            "ABW-electricity-demand_cts",
            "ABW-electricity-demand_ind",
        ],
    },
)
