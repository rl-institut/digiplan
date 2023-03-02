"""Views for map app.

As map app is SPA, this module contains main view and various API points.
"""
import json
import pathlib
import uuid

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from digiplan.map.config import config
from digiplan.map.results import core

from .forms import PanelForm, StaticLayerForm
from .mapset import setup
from .results import calculations


class MapGLView(TemplateView):
    """Main view for map app (SPA)."""

    template_name = "map.html"
    extra_context = {
        "debug": settings.DEBUG,
        "password_protected": settings.PASSWORD_PROTECTION,
        "password": settings.PASSWORD,
        "tiling_service_token": settings.TILING_SERVICE_TOKEN,
        "tiling_service_style_id": settings.TILING_SERVICE_STYLE_ID,
        "map_images": config.MAP_IMAGES,
        "map_layers": [layer.get_layer() for layer in setup.ALL_LAYERS],
        "layers_at_startup": setup.LAYERS_AT_STARTUP,
        "map_popups": setup.POPUPS,
        "area_switches": {
            category: [StaticLayerForm(layer) for layer in layers] for category, layers in setup.LEGEND.items()
        },
        "energy_settings_panel": PanelForm(config.ENERGY_SETTINGS_PANEL),
        "heat_settings_panel": PanelForm(config.HEAT_SETTINGS_PANEL),
        "traffic_settings_panel": PanelForm(config.TRAFFIC_SETTINGS_PANEL),
        "use_distilled_mvts": settings.USE_DISTILLED_MVTS,
        "store_hot_init": config.STORE_HOT_INIT,
        "zoom_levels": config.ZOOM_LEVELS,
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
        session_id = str(uuid.uuid4())
        context = super().get_context_data(**kwargs)
        context["session_id"] = session_id
        context["layer_styles"] = config.LAYER_STYLES
        context["settings_parameters"] = config.ENERGY_SETTINGS_PANEL
        context["settings_dependency_map"] = config.SETTINGS_DEPENDENCY_MAP
        context["dependency_parameters"] = config.DEPENDENCY_PARAMETERS

        # Sources need valid URL (containing host and port), thus they have to be defined using request:
        context["map_sources"] = {map_source.name: map_source.get_source(self.request) for map_source in setup.SOURCES}

        # Categorize sources
        categorized_sources = {
            category: [config.SOURCES[layer.layer.id] for layer in layers if layer.layer.id in config.SOURCES]
            for category, layers in setup.LEGEND.items()
        }
        context["sources"] = categorized_sources

        # Add popup-layer IDs to cold store
        config.STORE_COLD_INIT["popup_layers"] = setup.POPUPS
        config.STORE_COLD_INIT["region_layers"] = [
            layer.id for layer in setup.REGION_LAYERS if layer.id.startswith("fill")
        ]
        config.STORE_COLD_INIT["result_views"] = {}  # Placeholder for already downloaded results (used in results.js)
        context["store_cold_init"] = json.dumps(config.STORE_COLD_INIT)

        return context


def get_clusters(request: HttpRequest) -> JsonResponse:  # noqa: ARG001
    """Return cluster geojson.

    Parameters
    ----------
    request : HttpRequest
        Request from map to visualize clusters

    Returns
    -------
    JsonResponse
        Clusters as Geojson
    """
    try:
        with pathlib.Path(config.CLUSTER_GEOJSON_FILE).open("r", encoding="utf-8") as geojson_file:
            clusters = json.load(geojson_file)
    except FileNotFoundError:
        clusters = {}
    return JsonResponse(clusters)


def get_popup(request: HttpRequest, lookup: str, region: int) -> JsonResponse:  # noqa: ARG001
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
    data = calculations.create_data(lookup, region)
    chart = calculations.create_chart(lookup, region)

    try:
        html = render_to_string(f"popups/{lookup}.html", context=data)
    except TemplateDoesNotExist:
        html = render_to_string("popups/default.html", context=data)
    return JsonResponse({"html": html, "chart": chart})


# pylint: disable=W0613
def get_choropleth(request: HttpRequest, lookup: str, scenario: str) -> JsonResponse:  # noqa: ARG001
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
    fill_color = config.CHOROPLETHS.get_fill_color(lookup, list(values.values()))
    return JsonResponse({"values": values, "fill_color": fill_color})


def get_visualization(request: HttpRequest) -> JsonResponse:
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
    scenario_name = request.GET["scenario"]
    parameters_raw = request.GET.get("parameters")
    parameters = json.loads(parameters_raw) if parameters_raw else {}
    visualization = request.GET["visualization"]
    scenario = core.Scenario(scenario_name, parameters)
    vh = core.VisualizationHandler([scenario])
    vh.add(visualization)
    vh.run()
    return JsonResponse(vh[visualization])
