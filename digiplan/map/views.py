import json
import random
import uuid

from django.conf import settings
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
    MAP_IMAGES,
    SOURCES,
    STORE_COLD_INIT,
    STORE_HOT_INIT,
    ZOOM_LEVELS,
)

from . import models
from .forms import StaticLayerForm, WindAreaForm
from .layers import (
    ALL_LAYERS,
    ALL_SOURCES,
    LAYERS_CATEGORIES,
    POPUPS,
    RASTER_LAYERS,
    REGION_LAYERS,
)


class MapGLView(TemplateView):
    template_name = "map.html"
    extra_context = {
        "debug": DEBUG,
        "password_protected": PASSWORD_PROTECTION,
        "password": PASSWORD,
        "tiling_service_token": TILING_SERVICE_TOKEN,
        "tiling_service_style_id": TILING_SERVICE_STYLE_ID,
        "map_images": MAP_IMAGES,
        "all_layers": ALL_LAYERS,
        "raster_layers": RASTER_LAYERS,
        "all_sources": ALL_SOURCES,
        "popups": POPUPS,
        "region_filter": None,  # RegionFilterForm(),
        "area_switches": {
            category: [StaticLayerForm(layer) for layer in layers] for category, layers in LAYERS_CATEGORIES.items()
        },
        "energysystem": WindAreaForm(),
        "use_distilled_mvts": USE_DISTILLED_MVTS,
        "store_hot_init": STORE_HOT_INIT,
        "zoom_levels": ZOOM_LEVELS,
    }

    def get_context_data(self, **kwargs):
        # Add unique session ID
        session_id = str(uuid.uuid4())
        context = super().get_context_data(**kwargs)
        context["session_id"] = session_id

        # Add layer styles (used in map.html)
        with open(
            settings.APPS_DIR.path("static").path("styles").path("layer_styles.json"), "r", encoding="utf-8"
        ) as layer_styles:
            context["layer_styles"] = json.loads(layer_styles.read())

        # Add result styles (loaded in map.html, used in results.js)
        with open(
            settings.APPS_DIR.path("static").path("styles").path("result_styles.json"), "r", encoding="utf-8"
        ) as result_styles:
            context["result_styles"] = json.loads(result_styles.read())

        # Categorize sources
        categorized_sources = {
            category: [SOURCES[layer.source] for layer in layers if layer.source in SOURCES]
            for category, layers in LAYERS_CATEGORIES.items()
        }
        context["sources"] = categorized_sources

        # Add popup-layer IDs to cold store
        STORE_COLD_INIT["popup_layers"] = [popup.layer_id for popup in POPUPS]
        STORE_COLD_INIT["region_layers"] = [layer.id for layer in REGION_LAYERS if layer.id.startswith("fill")]
        STORE_COLD_INIT["result_views"] = []  # Placeholder for already downloaded results (used in results.js)
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
    # FIXME: Replace dummy data with actual data
    if result_view == "re_power_percentage":
        return JsonResponse(
            {
                municipality.id: random.randint(0, 100) / 100  # noqa: S311
                for municipality in models.Municipality.objects.all()
            }
        )
    if result_view == "re_power":
        return JsonResponse(
            {
                municipality.id: random.randint(0, 50) / 100  # noqa: S311
                for municipality in models.Municipality.objects.all()
            }
        )
    raise ValueError(f"Unknown result view '{result_view}'")
