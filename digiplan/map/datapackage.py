"""Read functionality for digipipe datapackage."""
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Optional

import pandas as pd
from django.conf import settings
from django_oemof.settings import OEMOF_DIR

from config.settings.base import DATA_DIR
from digiplan.map import config


def get_employment() -> pd.DataFrame:
    """Return employment data."""
    employment_filename = settings.DIGIPIPE_DIR.path("scalars").path("employment.csv")
    return pd.read_csv(employment_filename, index_col=0)


def get_batteries() -> pd.DataFrame:
    """Return battery data."""
    battery_filename = settings.DIGIPIPE_DIR.path("scalars").path("bnetza_mastr_storage_stats_muns.csv")
    return pd.read_csv(battery_filename)


def get_power_demand(sector: Optional[str] = None) -> dict[str, pd.DataFrame]:
    """Return power demand for given sector or all sectors."""
    sectors = (sector,) if sector else ("hh", "cts", "ind")
    demand = {}
    for sec in sectors:
        demand_filename = settings.DIGIPIPE_DIR.path("scalars").path(f"demand_{sec}_power_demand.csv")
        demand[sec] = pd.read_csv(demand_filename)
    return demand


def get_heat_demand(sector: Optional[str] = None) -> dict[str, pd.DataFrame]:
    """Return heat demand for given sector or all sectors."""
    sectors = (sector,) if sector else ("hh", "cts", "ind")
    demand = {}
    for sec in sectors:
        demand_filename = settings.DIGIPIPE_DIR.path("scalars").path(f"demand_{sec}_heat_demand.csv")
        demand[sec] = pd.read_csv(demand_filename)
    return demand


def get_heat_capacity_shares(distribution: str) -> dict:
    """Return capacity shares of heating structure."""
    shares_filename = settings.DIGIPIPE_DIR.path("scalars").path(f"demand_heat_structure_esys_{distribution}.csv")
    with Path(shares_filename).open("r", encoding="utf-8") as shares_file:
        reader = csv.DictReader(shares_file)
        shares = {}
        summed_shares = 0.0
        for row in reader:
            if row["year"] == "2022":
                continue
            if row["carrier"] == "heat_pump":
                continue
            shares[row["carrier"]] = float(row["demand_rel"])
            summed_shares += float(row["demand_rel"])
    return {k: v / summed_shares for k, v in shares.items()}


def get_summed_heat_demand_per_municipality(
    sector: Optional[str] = None,
    distribution: Optional[str] = None,
) -> dict[str, dict[str, pd.DataFrame]]:
    """Return heat demand for given sector and distribution."""
    sectors = (sector,) if sector else ("hh", "cts", "ind")
    distributions = (distribution,) if distribution else ("cen", "dec")
    demand = defaultdict(dict)
    for sec in sectors:
        for dist in distributions:
            demand_filename = settings.DIGIPIPE_DIR.path("scalars").path(
                f"demand_{sec}_heat_demand_{dist}.csv",
            )
            demand[sec][dist] = pd.read_csv(demand_filename)
    return demand


def get_heat_demand_profile(
    sector: Optional[str] = None,
    distribution: Optional[str] = None,
) -> dict[str, dict[str, pd.DataFrame]]:
    """Return heat demand for given sector and distribution."""
    sectors = (sector,) if sector else ("hh", "cts", "ind")
    distributions = (distribution,) if distribution else ("central", "decentral")
    demand = defaultdict(dict)
    for sec in sectors:
        for dist in distributions:
            demand_filename = (
                OEMOF_DIR / settings.OEMOF_SCENARIO / "data" / "sequences" / f"heat_{dist}-demand_{sec}_profile.csv"
            )
            demand[sec][dist] = pd.read_csv(demand_filename, sep=";")[f"ABW-heat_{dist}-demand_{sec}-profile"]
    return demand


def get_thermal_efficiency(component: str) -> float:
    """Return thermal efficiency from given component from oemof scenario."""
    component_filename = OEMOF_DIR / settings.OEMOF_SCENARIO / "data" / "elements" / f"{component}.csv"
    component_df = pd.read_csv(component_filename, sep=";")
    if component_df["type"][0] in ("extraction", "backpressure"):
        return float(pd.read_csv(component_filename, sep=";")["thermal_efficiency"][0])

    if "efficiency" in component_df.columns and isinstance(component_df["efficiency"][0], float):
        return component_df["efficiency"][0]

    if "heatpump" in component:
        component = "efficiency"
    sequence_filename = OEMOF_DIR / settings.OEMOF_SCENARIO / "data" / "sequences" / f"{component}_profile.csv"
    return pd.read_csv(sequence_filename, sep=";").iloc[:, 1]


def get_potential_values(*, per_municipality: bool = False) -> dict:
    """
    Calculate max_values for sliders.

    Parameters
    ----------
    per_municipality: bool
        If set to True, potentials are not aggregated, but given per municipality

    Returns
    -------
    dict
        dictionary with each slider / switch and respective max_value
    """
    scalars = {
        "wind": "potentialarea_wind_area_stats_muns.csv",
        "pv_ground": "potentialarea_pv_ground_area_stats_muns.csv",
        "pv_roof": "potentialarea_pv_roof_wo_historic_area_stats_muns.csv",
    }

    areas = {
        "wind": {
            "s_w_3": "stp_2018_vreg",
            "s_w_4_1": "stp_2027_vr",
            "s_w_4_2": "stp_2027_repowering",
            "s_w_5_1": "stp_2027_search_area_open_area",
            "s_w_5_2": "stp_2027_search_area_forest_area",
        },
        "pv_ground": {"s_pv_ff_3": "road_railway_region", "s_pv_ff_4": "agriculture_lfa-off_region"},
        "pv_roof": {"s_pv_d_3": None},
    }

    tech_data = json.load(Path.open(Path(settings.DIGIPIPE_DIR, "scalars/technology_data.json")))

    potentials = {}
    for profile in areas:
        path = Path(DATA_DIR, "digipipe/scalars", scalars[profile])
        reader = pd.read_csv(path)
        for key, value in areas[profile].items():
            if key == "s_pv_d_3":
                pv_roof_potential = reader[
                    [f"installable_power_{orient}" for orient in ["south", "east", "west", "flat"]]
                ].sum(axis=1)
                if per_municipality:
                    potentials = pv_roof_potential
                else:
                    potentials[key] = pv_roof_potential.sum()
            else:
                if per_municipality:
                    potentials[key] = reader[value]
                else:
                    potentials[key] = reader[value].sum()
                if profile == "wind":
                    potentials[key] = potentials[key] * tech_data["power_density"]["wind"]
                if profile == "pv_ground":
                    potentials[key] = potentials[key] * tech_data["power_density"]["pv_ground"]
    return potentials


def get_full_load_hours(year: int) -> pd.Series:
    """Return full load hours for given year."""
    full_load_hours = pd.Series(
        data=[technology_data[str(year)] for technology_data in config.TECHNOLOGY_DATA["full_load_hours"].values()],
        index=config.TECHNOLOGY_DATA["full_load_hours"].keys(),
    )
    return full_load_hours


def get_power_density(technology: Optional[str] = None) -> dict:
    """Return power density for technology."""
    if technology:
        return config.TECHNOLOGY_DATA["power_density"][technology]
    return config.TECHNOLOGY_DATA["power_density"]


def get_profile(technology: str) -> pd.Series:
    """Return profile for given technology from oemof datapackage."""
    profile_filename = OEMOF_DIR / settings.OEMOF_SCENARIO / "data" / "sequences" / f"{technology}_profile.csv"
    profile = pd.read_csv(profile_filename, sep=";", index_col=0)
    return profile.iloc[:, 0]
