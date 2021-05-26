import json
import uuid

from django.conf import settings
from django.views.generic import TemplateView

from .layers import (
    ALL_LAYERS,
    ALL_SOURCES,
    LAYERS_CATEGORIES,
)
from config.settings.base import (
    USE_DISTILLED_MVTS,
    PASSWORD_PROTECTION,
    PASSWORD,
    MAPBOX_TOKEN,
    MAPBOX_STYLE_LOCATION,
)
from .forms import StaticLayerForm
from .config import STORE_COLD_INIT, STORE_HOT_INIT, SOURCES


class MapGLView(TemplateView):
    template_name = "map.html"
    extra_context = {
        "password_protected": PASSWORD_PROTECTION,
        "password": PASSWORD,
        "mapbox_token": MAPBOX_TOKEN,
        "mapbox_style_location": MAPBOX_STYLE_LOCATION,
        "all_layers": ALL_LAYERS,
        "all_sources": ALL_SOURCES,
        "area_switches": {
            category: [StaticLayerForm(layer) for layer in layers]
            for category, layers in LAYERS_CATEGORIES.items()
        },
        "use_distilled_mvts": USE_DISTILLED_MVTS,
        "store_cold_init": STORE_COLD_INIT,
        "store_hot_init": STORE_HOT_INIT,
    }

    def get_context_data(self, **kwargs):
        session_id = str(uuid.uuid4())
        context = super(MapGLView, self).get_context_data(**kwargs)
        context["session_id"] = session_id
        with open(
            settings.APPS_DIR.path("static").path("styles").path("layer_styles.json"),
            "r",
        ) as regions:
            context["layer_styles"] = json.loads(regions.read())

        # Categorize sources
        categorized_sources = {
            category: [
                SOURCES[layer["source"]]
                for layer in layers
                if layer["source"] in SOURCES
            ]
            for category, layers in LAYERS_CATEGORIES.items()
        }

        context["sources"] = categorized_sources
        return context
