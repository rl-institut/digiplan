"""Module to implement hooks for django-oemof."""

import pandas
from django.http import HttpRequest

from .. import config, forms


def read_parameters(scenario: str, parameters: dict, request: HttpRequest) -> dict:
    """
    Read parameters from settings panel

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


def adapt_demand(scenario: str, data: dict, request: HttpRequest) -> dict:
    """
    Reads demand settings and scales and aggregates related demands

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
    demand_filename = config.SCENARIOS_DIR.path(scenario).path("demands.csv")
    demands = pandas.read_csv(demand_filename)
    electricity_demand = (
        demands.households * data["s_v_2"] / 100
        + demands.commerce * data["s_v_3"] / 100
        + demands.industry * data["s_v_4"] / 100
    )
    parameters = {"demand0": {"profile": electricity_demand.tolist()}}
    return parameters
