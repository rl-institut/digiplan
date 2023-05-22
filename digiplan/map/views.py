"""Views for map app.

As map app is SPA, this module contains main view and various API points.
"""

from django.conf import settings
from django.http import HttpRequest, response
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django_mapengine import views

from digiplan.map import calculations, config
from digiplan.map.results import core

from . import charts, forms, map_config, popups, utils


class MapGLView(TemplateView, views.MapEngineMixin):
    """Main view for map app (SPA)."""

    template_name = "map.html"
    extra_context = {
        "debug": settings.DEBUG,
        "password_protected": settings.PASSWORD_PROTECTION,
        "password": settings.PASSWORD,
        "area_switches": {
            category: [forms.StaticLayerForm(layer) for layer in layers]
            for category, layers in map_config.LEGEND.items()
        },
        "store_hot_init": config.STORE_HOT_INIT,
        "oemof_scenario": settings.OEMOF_SCENARIO,
    }

    def get_context_data(self, **kwargs) -> dict:
        """Context data for main view.

        Parameters
        ----------
        kwargs
            Optional kwargs

        Returns
        -------
        dict
            context for main view
        """
        # Add unique session ID
        context = super().get_context_data(**kwargs)

        context["panels"] = [
            forms.EnergyPanelForm(utils.get_translated_json_from_file(config.ENERGY_SETTINGS_PANEL_FILE, self.request)),
            forms.HeatPanelForm(utils.get_translated_json_from_file(config.HEAT_SETTINGS_PANEL_FILE, self.request)),
            forms.TrafficPanelForm(
                utils.get_translated_json_from_file(config.TRAFFIC_SETTINGS_PANEL_FILE, self.request)
            ),
        ]

        context["settings_parameters"] = config.ENERGY_SETTINGS_PANEL
        context["settings_dependency_map"] = config.SETTINGS_DEPENDENCY_MAP
        context["dependency_parameters"] = config.DEPENDENCY_PARAMETERS

        # Categorize sources
        categorized_sources = {
            category: [
                config.SOURCES[layer.get_layer_id()] for layer in layers if layer.get_layer_id() in config.SOURCES
            ]
            for category, layers in map_config.LEGEND.items()
        }
        context["sources"] = categorized_sources
        context["store_cold_init"] = config.STORE_COLD_INIT
        context["detailed_overview"] = charts.create_chart("detailed_overview")

        return context


def get_popup(request: HttpRequest, lookup: str, region: int) -> response.JsonResponse:  # noqa: ARG001
    """Return popup as html and chart options to render chart on popup.

    Parameters
    ----------
    request : HttpRequest
        Request from app, can hold option for different language
    lookup: str
        Name is used to lookup data and chart functions
    region: int
        ID of region selected on map. Data and chart for popup is calculated for related region.

    Returns
    -------
    JsonResponse
        containing HTML to render popup and chart options to be used in E-Chart.
    """
    map_state = request.GET.dict()

    if lookup in popups.POPUPS:
        popup = popups.POPUPS[lookup](lookup, region, map_state)
        return popup.render()

    data = calculations.create_data(lookup, region, map_state)
    chart_data = charts.CHARTS[lookup](region)
    chart = charts.create_chart(lookup, chart_data)

    try:
        html = render_to_string(f"popups/{lookup}.html", context=data)
    except TemplateDoesNotExist:
        html = render_to_string("popups/default.html", context=data)
    return response.JsonResponse({"html": html, "chart": chart})


# pylint: disable=W0613
def get_choropleth(request: HttpRequest, lookup: str, scenario: str) -> response.JsonResponse:  # noqa: ARG001
    """Read scenario results from database, aggregate data and send back data.

    Parameters
    ----------
    request : HttpRequest
        Request can contain optional values (i.e. language)
    lookup : str
        which result/calculation shall be shown in choropleth?
    scenario : str
        defines the scenario to look up values for (i.e. status quo or user scenario)

    Returns
    -------
    JsonResponse
        Containing key-value pairs of municipality_ids and values and related color style
    """
    values = calculations.create_choropleth_data(lookup)
    fill_color = settings.MAP_ENGINE_CHOROPLETH_STYLES.get_fill_color(lookup, list(values.values()))
    return response.JsonResponse({"values": values, "paintProperties": {"fill-color": fill_color, "fill-opacity": 1}})


def get_visualization(request: HttpRequest) -> response.JsonResponse:
    """Return visualization from oemof simulation result.

    Parameters
    ----------
    request : HttpRequest
        Request for visualization

    Returns
    -------
    JsonResponse
        Visualization of simulation result
    """
    simulation_ids = [int(sim_id) for sim_id in request.GET.getlist("simulation_ids")]
    visualization = request.GET["visualization"]
    vh = core.VisualizationHandler(simulation_ids)
    vh.add(visualization)
    vh.run()
    return response.JsonResponse(vh[visualization])
