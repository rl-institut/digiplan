import json
import random
import uuid

from django.http import JsonResponse
from django.views.generic import TemplateView

from config.settings.base import (
    DEBUG,
    PASSWORD,
    PASSWORD_PROTECTION,
    TILING_SERVICE_STYLE_ID,
    TILING_SERVICE_TOKEN,
    USE_DISTILLED_MVTS,
)
from digiplan.map.config.config import (
    CLUSTER_GEOJSON_FILE,
    DEPENDENCY_PARAMETERS,
    ENERGY_SETTINGS_PANEL,
    HEAT_SETTINGS_PANEL,
    LAYER_STYLES,
    MAP_IMAGES,
    RESULTS_CHOROPLETHS,
    SETTINGS_DEPENDENCY_MAP,
    SOURCES,
    STORE_COLD_INIT,
    STORE_HOT_INIT,
    TRAFFIC_SETTINGS_PANEL,
    ZOOM_LEVELS,
)
from digiplan.map.results import core

from . import models
from .forms import PanelForm, StaticLayerForm
from .mapset import setup


class MapGLView(TemplateView):
    template_name = "map.html"
    extra_context = {
        "debug": DEBUG,
        "password_protected": PASSWORD_PROTECTION,
        "password": PASSWORD,
        "tiling_service_token": TILING_SERVICE_TOKEN,
        "tiling_service_style_id": TILING_SERVICE_STYLE_ID,
        "map_images": MAP_IMAGES,
        "map_layers": [layer.get_layer() for layer in setup.ALL_LAYERS],
        "layers_at_startup": setup.LAYERS_AT_STARTUP,
        "popups": setup.POPUPS,
        "area_switches": {
            category: [StaticLayerForm(layer) for layer in layers] for category, layers in setup.LEGEND.items()
        },
        "energy_settings_panel": PanelForm(ENERGY_SETTINGS_PANEL),
        "heat_settings_panel": PanelForm(HEAT_SETTINGS_PANEL),
        "traffic_settings_panel": PanelForm(TRAFFIC_SETTINGS_PANEL),
        "use_distilled_mvts": USE_DISTILLED_MVTS,
        "store_hot_init": STORE_HOT_INIT,
        "zoom_levels": ZOOM_LEVELS,
    }

    def get_context_data(self, **kwargs):
        # Add unique session ID
        session_id = str(uuid.uuid4())
        context = super().get_context_data(**kwargs)
        context["session_id"] = session_id
        context["layer_styles"] = LAYER_STYLES
        context["settings_parameters"] = ENERGY_SETTINGS_PANEL
        context["settings_dependency_map"] = SETTINGS_DEPENDENCY_MAP
        context["dependency_parameters"] = DEPENDENCY_PARAMETERS

        # Sources need valid URL (containing host and port), thus they have to be defined using request:
        context["map_sources"] = {map_source.name: map_source.get_source(self.request) for map_source in setup.SOURCES}

        # Categorize sources
        categorized_sources = {
            category: [SOURCES[layer.layer.id] for layer in layers if layer.layer.id in SOURCES]
            for category, layers in setup.LEGEND.items()
        }
        context["sources"] = categorized_sources

        # Add popup-layer IDs to cold store
        STORE_COLD_INIT["popup_layers"] = [popup.layer_id for popup in setup.POPUPS]
        STORE_COLD_INIT["region_layers"] = [layer.id for layer in setup.REGION_LAYERS if layer.id.startswith("fill")]
        STORE_COLD_INIT["result_views"] = {}  # Placeholder for already downloaded results (used in results.js)
        context["store_cold_init"] = json.dumps(STORE_COLD_INIT)

        return context


def get_clusters(request):
    try:
        with open(CLUSTER_GEOJSON_FILE, "r", encoding="utf-8") as geojson_file:
            clusters = json.load(geojson_file)
    except FileNotFoundError:
        clusters = {}
    return JsonResponse(clusters)


def get_results(request):
    """
    Reads scenario results from database, aggregates data according to results view and sends back data
    related to municipality.

    Parameters
    ----------
    request : HttpRequest
        Request must contain GET variables "scenario_id" and "result_view"

    Returns
    -------
    dict
        Containing key-value pairs of municipality_ids and values

    Raises
    ------
    ValueError
        If result view is unknown
    """
    # pylint: disable=W0511,W0612
    scenario_id = request.GET["scenario_id"]  # noqa: F841
    result_view = request.GET["result_view"]

    if result_view == "EinwohnerInnen":
        values = {
            row.municipality_id: row.value
            for row in models.Population.objects.filter(year=2022)
        }
        fill_color = RESULTS_CHOROPLETHS.get_fill_color(result_view, list(values.values()))
        return JsonResponse({"values": values, "fill_color": fill_color})

    # FIXME: Replace dummy data with actual data
    if result_view == "re_power_percentage":
        values = {
            municipality.id: random.randint(0, 100) / 100  # noqa: S311
            for municipality in models.Municipality.objects.all()
        }
        fill_color = RESULTS_CHOROPLETHS.get_fill_color(result_view)
        return JsonResponse({"values": values, "fill_color": fill_color})
    if result_view == "re_power":
        values = {
            municipality.id: random.randint(0, 100) / 100  # noqa: S311
            for municipality in models.Municipality.objects.all()
        }
        fill_color = RESULTS_CHOROPLETHS.get_fill_color(result_view, list(values.values()))
        return JsonResponse({"values": values, "fill_color": fill_color})
    raise ValueError(f"Unknown result view '{result_view}'")


def get_visualization(request):
    scenario_name = request.GET["scenario"]
    parameters_raw = request.GET.get("parameters")
    parameters = json.loads(parameters_raw) if parameters_raw else {}
    visualization = request.GET["visualization"]
    scenario = core.Scenario(scenario_name, parameters)
    vh = core.VisualizationHandler([scenario])
    vh.add(visualization)
    vh.run()
    return JsonResponse(vh[visualization])
