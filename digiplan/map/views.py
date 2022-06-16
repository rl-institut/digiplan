import json
import uuid

from django.conf import settings
from django.views.generic import TemplateView
from django.http import JsonResponse

from .layers import ALL_LAYERS, REGION_LAYERS, RASTER_LAYERS, ALL_SOURCES, LAYERS_CATEGORIES, POPUPS
from config.settings.base import (
    DEBUG,
    USE_DISTILLED_MVTS,
    PASSWORD_PROTECTION,
    PASSWORD,
    MAPBOX_TOKEN,
    MAPBOX_STYLE_LOCATION,
)
from .forms import StaticLayerForm  # , RegionFilterForm
from .config import STORE_COLD_INIT, STORE_HOT_INIT, SOURCES, MAP_IMAGES, CLUSTER_GEOJSON_FILE, ZOOM_LEVELS
from . import models
from django.contrib.gis.db.models import functions


class MapGLView(TemplateView):
    template_name = "map.html"
    extra_context = {
        "debug": DEBUG,
        "password_protected": PASSWORD_PROTECTION,
        "password": PASSWORD,
        "mapbox_token": MAPBOX_TOKEN,
        "mapbox_style_location": MAPBOX_STYLE_LOCATION,
        "map_images": MAP_IMAGES,
        "all_layers": ALL_LAYERS,
        "raster_layers": RASTER_LAYERS,
        "all_sources": ALL_SOURCES,
        "popups": POPUPS,
        "region_filter": None,  # RegionFilterForm(),
        "area_switches": {
            category: [StaticLayerForm(layer) for layer in layers] for category, layers in LAYERS_CATEGORIES.items()
        },
        "use_distilled_mvts": USE_DISTILLED_MVTS,
        "store_hot_init": STORE_HOT_INIT,
        "zoom_levels": ZOOM_LEVELS,
    }

    def get_context_data(self, **kwargs):
        # Add unique session ID
        session_id = str(uuid.uuid4())
        context = super(MapGLView, self).get_context_data(**kwargs)
        context["session_id"] = session_id

        # Add layer styles
        with open(
            settings.APPS_DIR.path("static").path("styles").path("layer_styles.json"),
            "r",
        ) as regions:
            context["layer_styles"] = json.loads(regions.read())

        # Categorize sources
        categorized_sources = {
            category: [SOURCES[layer.source] for layer in layers if layer.source in SOURCES]
            for category, layers in LAYERS_CATEGORIES.items()
        }
        context["sources"] = categorized_sources

        # Add popup-layer IDs to cold store
        STORE_COLD_INIT["popup_layers"] = [popup.layer_id for popup in POPUPS]
        STORE_COLD_INIT["region_layers"] = [layer.id for layer in REGION_LAYERS if layer.id.startswith("fill")]
        context["store_cold_init"] = json.dumps(STORE_COLD_INIT)

        return context


def get_clusters(request):
    with open(CLUSTER_GEOJSON_FILE, "r") as geojson_file:
        clusters = json.load(geojson_file)
        return JsonResponse(clusters)


def get_state(request):
    state_name = request.GET["state"]
    state = models.State.objects.filter(name=state_name).annotate(center=functions.Centroid("geom"))
    districts = models.District.objects.filter(state__name=state_name).order_by("name").values_list("name", flat=True)
    return JsonResponse({"center": (state.first().center.x, state.first().center.y), "districts": list(districts)})


def get_district(request):
    district_name = request.GET["district"]
    district = models.District.objects.filter(name=district_name).annotate(center=functions.Centroid("geom"))
    return JsonResponse({"center": (district.first().center.x, district.first().center.y)})