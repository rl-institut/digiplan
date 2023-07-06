"""Read functionality for digipipe datapackage."""

from collections import defaultdict
from typing import Optional

import pandas as pd
from django.conf import settings


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
    sectors = tuple(sector) if sector else ("hh", "cts", "ind")
    demand = {}
    for sec in sectors:
        demand_filename = settings.DIGIPIPE_DIR.path("scalars").path(f"demand_{sec}_power_demand.csv")
        demand[sec] = pd.read_csv(demand_filename)
    return demand


def get_heat_demand(
    sector: Optional[str] = None,
    distribution: Optional[str] = None,
) -> dict[str, dict[str, pd.DataFrame]]:
    """Return heat demand for given sector and distribution."""
    sectors = tuple(sector) if sector else ("hh", "cts", "ind")
    distributions = tuple(distribution) if distribution else ("cen", "dec")
    demand = defaultdict(dict)
    for sec in sectors:
        for dist in distributions:
            demand_filename = settings.DIGIPIPE_DIR.path("scalars").path(
                f"demand_{sec}_heat_demand_{dist}.csv",
            )
            demand[sec][dist] = pd.read_csv(demand_filename)
    return demand
