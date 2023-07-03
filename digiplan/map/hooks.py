"""Module to implement hooks for django-oemof."""

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
    year = "2045" if scenario == "scenario_2045" else "2022"
    for sector, slider in (("hh", "s_v_2"), ("cts", "s_v_3"), ("ind", "s_v_4")):
        demand = datapackage.get_power_demand(sector)[sector]
        data[f"ABW-electricity-demand_{sector}"] = {"amount": float(demand[year].sum()) * data.pop(slider) / 100}
    return data


def adapt_heat_demand(scenario: str, data: dict, request: HttpRequest) -> dict:  # noqa: ARG001
    """
    Read settings and adapt related heat demands.

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
        Parameters for oemof with adapted heat demands
    """
    year = "2045" if scenario == "scenario_2045" else "2022"
    for sector, slider in (("hh", "w_v_3"), ("cts", "w_v_4"), ("ind", "w_v_5")):
        percentage = data.pop(slider)
        for distribution, distribution_name in (("cen", "central"), ("dec", "decentral")):
            demand = datapackage.get_heat_demand(sector, distribution)[sector][distribution]
            data[f"ABW-heat_{distribution_name}-demand_{sector}"] = {
                "amount": float(demand[year].sum()) * percentage / 100,
            }
    return data


def adapt_capacities(scenario: str, data: dict, request: HttpRequest) -> dict:  # noqa: ARG001
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
    # ELECTRICITY
    data["ABW-wind-onshore"] = {"capacity": data.pop("s_w_1")}
    data["ABW-solar-pv_ground"] = {"capacity": data.pop("s_pv_ff_1")}
    data["ABW-solar-pv_rooftop"] = {"capacity": data.pop("s_pv_d_1")}
    data["ABW-hydro-ror"] = {"capacity": data.pop("s_h_1")}
    data["ABW-electricity-large_scale_battery"] = {"capacity": data.pop("s_s_g_1")}

    data["ABW-electricity-heatpump_decentral"] = {"capacity": data.pop("w_d_wp_1")}
    data["ABW-electricity-heatpump_central"] = {"capacity": data.pop("w_z_wp_1")}

    # TODO(Hendrik): Get values either from static file or from sliders
    # https://github.com/rl-institut-private/digipipe/issues/119
    data["ABW-biogas-bpchp_central"] = {"capacity": 100}
    data["ABW-biogas-bpchp_decentral"] = {"capacity": 100}
    data["ABW-wood-extchp_central"] = {"capacity": 100}
    data["ABW-wood-extchp_decentral"] = {"capacity": 100}
    data["ABW-ch4-bpchp_central"] = {"capacity": 100}
    data["ABW-ch4-bpchp_decentral"] = {"capacity": 100}
    data["ABW-ch4-extchp_central"] = {"capacity": 100}
    data["ABW-ch4-extchp_decentral"] = {"capacity": 100}
    data["ABW-ch4-gt"] = {"capacity": 100}
    data["ABW-biogas-biogas_upgrading_plant"] = {"capacity": 100}
    data["ABW-biomass-biogas_plant"] = {"capacity": 100}
    return data
