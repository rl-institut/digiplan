"""
Views for map app.

As map app is SPA, this module contains main view and various API points.
"""

from django.conf import settings
from django.http import HttpRequest, response
from django.views.generic import TemplateView
from django_mapengine import views

from digiplan.map import config

from . import charts, choropleths, forms, map_config, popups, utils


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
        """
        Context data for main view.

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
                utils.get_translated_json_from_file(config.TRAFFIC_SETTINGS_PANEL_FILE, self.request),
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
        context["ghg_overview"] = charts.create_chart("ghg_overview")
        context["electricity_overview"] = charts.create_chart("electricity_overview")
        context["electricity_ghg"] = charts.create_chart("electricity_ghg")
        context["mobility_overview"] = charts.create_chart("mobility_overview")
        context["mobility_ghg"] = charts.create_chart("mobility_ghg")
        context["overview_heat"] = charts.create_chart("overview_heat")
        context["decentralized_centralized_heat"] = charts.create_chart("decentralized_centralized_heat")

        return context


def get_popup(request: HttpRequest, lookup: str, region: int) -> response.JsonResponse:
    """
    Return popup as html and chart options to render chart on popup.

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
    popup = popups.POPUPS[lookup](lookup, region, map_state)
    return popup.render()


# pylint: disable=W0613
def get_choropleth(request: HttpRequest, lookup: str, layer_id: str) -> response.JsonResponse:  # noqa: ARG001
    """
    Read scenario results from database, aggregate data and send back data.

    Parameters
    ----------
    request : HttpRequest
        Request can contain optional values (i.e. language)
    lookup : str
        which result/calculation shall be shown in choropleth?
    layer_id : str
        layer ID of given choropleth

    Returns
    -------
    JsonResponse
        Containing key-value pairs of municipality_ids and values and related color style
    """
    map_state = request.GET.dict()
    return choropleths.CHOROPLETHS[lookup](lookup, map_state)


def get_charts(request: HttpRequest) -> response.JsonResponse:
    """
    Return all result charts at once.

    Parameters
    ----------
    request: HttpRequest
        request holding simulation ID in map_state dict

    Returns
    -------
    JsonResponse
        holding dict with `div_id` as keys and chart options as values.
        `div_id` is used in frontend to detect chart container.
    """
    map_state = request.GET.dict()
    simulation_id = map_state["simulation_id"]
    return response.JsonResponse(
        {
            chart.div_id: chart.chart(simulation_id).render()
            for chart in charts.RESULT_CHARTS
        },
    )
