"""Module for calculations used for settings."""

import json
from pathlib import Path

import pandas as pd

from config.settings.base import DATA_DIR

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

max_values = {
    "s_w_3": 0,
    "s_w_4_1": 0,
    "s_w_4_2": 0,
    "s_w_5_1": 0,
    "s_w_5_2": 0,
    "s_pv_ff_3": 0,
    "s_pv_ff_4": 0,
    "s_pv_d_3": 0,
}


def get_max_values() -> dict:
    """
    Calculate max_values for sliders.

    Returns
    -------
    dict
        dictionary with each slider / switch and respective max_value
    """
    tech_data = json.load(Path.open(Path(DATA_DIR, "digipipe/scalars/technology_data.json")))
    for profile in areas:
        path = Path(DATA_DIR, "digipipe/scalars", scalars[profile])
        reader = pd.read_csv(path)
        for key, value in areas[profile].items():
            if key == "s_pv_d_3":
                max_values[key] = (
                    reader[[f"installable_power_{orient}" for orient in ["south", "east", "west", "flat"]]].sum().sum()
                )
            else:
                max_values[key] = reader[value].sum()
                if profile == "wind":
                    max_values[key] = max_values[key] * tech_data["power_density"]["wind"]
                if profile == "pv_ground":
                    max_values[key] = max_values[key] * tech_data["power_density"]["pv_ground"]
    return max_values
