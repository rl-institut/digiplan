"""Module to implement hooks for django-oemof."""

import json

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
    # since we only have 1 scenario, do we need the scenario argument here?
    filename = "absolute_values.json"
    absolute_filename = config.SCENARIOS_DIR.path(scenario).path(filename)
    # also why is the request as argument needed?

    with open(absolute_filename, "r") as read_file:
        jsondata = json.load(read_file)

    # since this will be one hook for all profiles(?), thats what I intent for later
    # like this, "electricity_demand" will be replaced by "profile"

    # for profile in jsondata.keys():
    region_values_per_sector = {
        "hh": sum(jsondata["electricity_demand"]["hh"]),
        "ghd": sum(jsondata["electricity_demand"]["ghd"]),
        "i": sum(jsondata["electricity_demand"]["i"]),
    }

    electricity_demand = [
        region_values_per_sector["hh"] * data["s_v_2"] / 100
        + region_values_per_sector["ghd"] * data["s_v_3"] / 100
        + region_values_per_sector["i"] * data["s_v_4"] / 100
    ]
    parameters = {"demand0": {"profile": electricity_demand}}
    return parameters
