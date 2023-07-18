"""Module for calculations used for choropleths or charts."""

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


def electricity_demand_per_municipality() -> pd.DataFrame:
    """
    Calculate electricity demand per sector per municipality in GWh.

    Returns
    -------
    pd.DataFrame
        Electricity demand per municipality (index) and sector (column)
    """
    demands_raw = datapackage.get_power_demand()
    demands_per_sector = pd.concat([demand["2022"] for demand in demands_raw.values()], axis=1)
    demands_per_sector.columns = [
        _("Electricity Household Demand"),
        _("Electricity CTS Demand"),
        _("Electricity Industry Demand"),
    ]
    # TODO (Hendrik): Integrate BEV
    # https://github.com/rl-institut-private/digiplan/issues/315
    demands_per_sector["BEV"] = 0
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
    # TODO (Hendrik): Read BEV data from datapackage
    # https://github.com/rl-institut-private/digiplan/issues/315
    demands_per_sector["bev"] = pd.DataFrame({"2045": [1] * 20})
    mappings = {
        "bev": "ABW-electricity-bev_charging",
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

    demand = results["electricity_demand"][
        results["electricity_demand"].index.get_level_values(1).isin(config.SIMULATION_DEMANDS)
    ]
    demand.index = demand.index.get_level_values(1)

    electricity_heat_production_result = electricity_heat_demand(simulation_id)
    demand["ABW-electricity-demand_hh"] += electricity_heat_production_result["electricity_heat_demand_hh"]
    demand["ABW-electricity-demand_cts"] += electricity_heat_production_result["electricity_heat_demand_cts"]
    demand["ABW-electricity-demand_ind"] += electricity_heat_production_result["electricity_heat_demand_ind"]
    overview_data = pd.concat([renewables, demand])
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
            "ABW-electricity-bev_charging",
        ),
    )
    overview_data = overview_data * 1e-3
    return overview_data


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
