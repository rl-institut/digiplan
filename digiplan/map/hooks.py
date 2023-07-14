"""Module to implement hooks for django-oemof."""

import logging
import math

import pandas as pd
from django.http import HttpRequest

from digiplan.map import config, datapackage, forms


def read_parameters(scenario: str, parameters: dict, request: HttpRequest) -> dict:  # noqa: ARG001
    """
    Read parameters from settings panel.

    Parameters
    ----------
    scenario: str
        Used oemof scenario
    parameters: dict
        Empty dict as parameters are initialized here.
    request: HttpRequest
        Original request from settings panel submit

    Returns
    -------
    dict
        Initial parameters read from settings panel

    Raises
    ------
    ValueError
        if one of the panel forms is invalid
    """
    panel_forms = [
        forms.EnergyPanelForm(config.ENERGY_SETTINGS_PANEL, data=request.POST),
        forms.HeatPanelForm(config.HEAT_SETTINGS_PANEL, data=request.POST),
        forms.TrafficPanelForm(config.TRAFFIC_SETTINGS_PANEL, data=request.POST),
    ]
    for form in panel_forms:
        if not form.is_valid():
            raise ValueError(f"Invalid settings form.\nErrors: {form.errors}")
        parameters.update(**form.cleaned_data)
    return parameters


def adapt_electricity_demand(scenario: str, data: dict, request: HttpRequest) -> dict:  # noqa: ARG001
    """
    Read demand settings and scales and aggregates related demands.

    Parameters
    ----------
    scenario: str
        Used oemof scenario
    data : dict
        Raw parameters from user settings
    request : HttpRequest
        Original request from settings

    Returns
    -------
    dict
        Parameters for oemof with adapted demands
    """
    del data["s_v_1"]
    year = "2045" if scenario == "scenario_2045" else "2022"
    for sector, slider in (("hh", "s_v_3"), ("cts", "s_v_4"), ("ind", "s_v_5")):
        demand = datapackage.get_power_demand(sector)[sector]
        logging.info(f"Adapting electricity demand at {sector=}.")
        data[f"ABW-electricity-demand_{sector}"] = {"amount": float(demand[year].sum()) * data.pop(slider) / 100}
    return data


def adapt_heat_capacities(distribution: str, remaining_energy: pd.Series) -> dict:
    """Adapt heat settings for remaining energy."""
    # TODO (Hendrik): Read values from datapackage  # noqa: TD003
    heat_shares = {
        "central": {
            "ABW-wood-extchp_central": 0,
            "ABW-biogas-bpchp_central": 0,
            "ABW-ch4-bpchp_central": 0.5,
            "ABW-ch4-extchp_central": 0.5,
            "ABW-solar-thermalcollector_central": 0,
            "ABW-ch4-boiler_central": 0,
        },
        "decentral": {
            "ABW-wood-extchp_decentral": 0.15,
            "ABW-biogas-bpchp_decentral": 0.15,
            "ABW-ch4-bpchp_decentral": 0.15,
            "ABW-ch4-extchp_decentral": 0.30,
            "ABW-solar-thermalcollector_decentral": 0,
            "ABW-ch4-boiler_decentral": 0.15,
            "ABW-wood-oven": 0.1,
        },
    }

    remaining_energy_sum = remaining_energy.sum()
    data = {}
    for component, share in heat_shares[distribution].items():
        if share == 0:
            continue
        efficiency = datapackage.get_thermal_efficiency(component[4:])
        capacity = math.ceil((remaining_energy / efficiency).max() * share)
        if capacity == 0:
            continue
        energy = remaining_energy_sum * share
        if "extchp" in component or "bpchp" in component:
            parameter = "input_parameters"
            energy = energy / efficiency
        else:
            parameter = "output_parameters"
        logging.info(f"Adapting capacity and energy for {component} at {distribution=}.")
        data[component] = {
            "capacity": capacity,
            parameter: {
                "summed_min": energy / capacity,
                "summed_max": energy / capacity,
            },
        }
    return data


def adapt_heat_settings(scenario: str, data: dict, request: HttpRequest) -> dict:  # noqa: ARG001
    """
    Read settings and adapt related heat demands and capacities.

    Parameters
    ----------
    scenario: str
        Used oemof scenario
    data : dict
        Raw parameters from user settings
    request : HttpRequest
        Original request from settings

    Returns
    -------
    dict
        Parameters for oemof with adapted heat demands and capacities
    """
    demand_sliders = {"hh": "w_v_3", "cts": "w_v_4", "ind": "w_v_5"}
    hp_sliders = {"hh": "w_d_wp_3", "cts": "w_d_wp_4", "ind": "w_d_wp_5"}

    heat_demand_per_municipality = datapackage.get_summed_heat_demand_per_municipality()
    heat_demand = datapackage.get_heat_demand()

    for distribution in ("central", "decentral"):
        demand = {}
        hp_energy = {}

        # Calculate demands per sector
        for sector in ("hh", "cts", "ind"):
            summed_demand = int(  # Convert to int, otherwise int64 is used
                heat_demand_per_municipality[sector][distribution[:3]]["2045"].sum(),
            )
            demand[sector] = heat_demand[sector][distribution] * summed_demand
            percentage = (
                data.pop(demand_sliders[sector]) if distribution == "decentral" else data.get(demand_sliders[sector])
            )
            # DEMAND
            logging.info(f"Adapting heat demand at {distribution=} and {sector=}.")
            data[f"ABW-heat_{distribution}-demand_{sector}"] = {
                "amount": summed_demand * percentage / 100,
            }

            # HP contribution per sector:
            if distribution == "decentral":
                hp_share = data.pop(hp_sliders[sector]) / 100
                hp_energy[sector] = demand[sector] * hp_share
            else:
                if sector == "hh":  # noqa: PLR5501
                    hp_share = data.pop("w_z_wp_3") / 100
                    hp_energy[sector] = demand[sector] * hp_share
                else:
                    hp_energy[sector] = demand[sector] * 0

        # HP Capacity and Energies
        hp_energy_total = pd.concat(hp_energy.values(), axis=1).sum(axis=1)
        hp_energy_sum = hp_energy_total.sum()
        capacity = math.ceil(hp_energy_total.max())
        logging.info(f"Adapting capacity and energy for heatpump at {distribution=}.")
        data[f"ABW-electricity-heatpump_{distribution}"] = {
            "capacity": capacity,
            "output_parameters": {
                "summed_min": hp_energy_sum / capacity,
                "summed_max": hp_energy_sum / capacity,
            },
        }

        total_demand = pd.concat(demand.values(), axis=1).sum(axis=1)
        remaining_energy = total_demand - hp_energy_total

        # HEAT capacities
        data.update(adapt_heat_capacities(distribution, remaining_energy))

        # STORAGES
        storage_sliders = {"decentral": "w_d_s_1", "central": "w_z_s_1"}
        avg_demand_per_day = total_demand.sum() / 365
        logging.info(f"Adapting capacity for storage at {distribution=}.")
        data[f"ABW-heat_{distribution}-storage"] = {
            "capacity": float(avg_demand_per_day * data.pop(storage_sliders[distribution]) / 100),
        }

    # Remove unnecessary heat settings
    del data["w_v_1"]
    del data["w_d_wp_1"]
    del data["w_z_wp_1"]
    del data["w_d_s_3"]
    del data["w_z_s_3"]

    return data


def adapt_renewable_capacities(scenario: str, data: dict, request: HttpRequest) -> dict:  # noqa: ARG001
    """
    Read renewable capacities from user input and adapt ES parameters accordingly.

    Parameters
    ----------
    scenario: str
        Name of oemof datapackage
    data: dict
        User-given input parameters
    request:
        HttpRequest from django

    Returns
    -------
    dict
        Adapted parameters dict with set up capacities
    """
    # Capacities
    data["ABW-wind-onshore"] = {"capacity": data.pop("s_w_1")}
    data["ABW-solar-pv_ground"] = {"capacity": data.pop("s_pv_ff_1")}
    data["ABW-solar-pv_rooftop"] = {"capacity": data.pop("s_pv_d_1")}
    data["ABW-hydro-ror"] = {"capacity": data.pop("s_h_1")}
    data["ABW-electricity-large_scale_battery"] = {"capacity": data.pop("s_s_g_1")}

    # Full load hours
    technology_mapping = {
        "ABW-wind-onshore": "wind",
        "ABW-solar-pv_ground": "pv_ground",
        "ABW-solar-pv_rooftop": "pv_roof",
        "ABW-hydro-ror": "ror",
    }
    full_load_hours = datapackage.get_full_load_hours(2045)
    for technology, mapped_key in technology_mapping.items():
        data[technology]["profile"] = datapackage.get_profile(technology[4:]) * full_load_hours[mapped_key]

    # Remove unnecessary renewable sliders:
    del data["s_w_3"]
    del data["s_w_4"]
    del data["s_w_4_1"]
    del data["s_w_4_2"]
    del data["s_w_5"]
    del data["s_w_5_1"]
    del data["s_w_5_2"]
    del data["s_pv_ff_3"]
    del data["s_pv_ff_4"]
    del data["s_pv_d_3"]
    del data["s_pv_d_4"]
    return data
