"""Read functionality for digipipe datapackage."""

from collections import defaultdict
from typing import Optional

import pandas as pd
from django.conf import settings
from django_oemof.settings import OEMOF_DIR


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


def get_heat_demand(
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
