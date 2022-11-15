from django.conf import settings
from django.urls import path
from django_distill import distill_path

from digiplan.map.config.config import get_tile_coordinates_for_region

from . import views
from .mvt import mvt_view_factory
from .mvt_layers import DISTILL_MVT_LAYERS, MVT_LAYERS

app_name = "map"

urlpatterns = [
    path("", views.MapGLView.as_view(), name="map"),
    path("clusters", views.get_clusters, name="clusters"),
    path("results", views.get_results, name="results"),
    path("visualization", views.get_visualization, name="visualization"),
]

urlpatterns += [
    path(f"{name}_mvt/<int:z>/<int:x>/<int:y>/", mvt_view_factory(name, layers)) for name, layers in MVT_LAYERS.items()
]


def get_all_statics_for_state_lod(view_name):
    for x, y, z in get_tile_coordinates_for_region(view_name):
        yield z, x, y


# Distill MVT-urls:
if settings.DISTILL:
    urlpatterns += [
        distill_path(
            f"<int:z>/<int:x>/<int:y>/{name}.mvt",
            mvt_view_factory(name, layers),
            name=name,
            distill_func=get_all_statics_for_state_lod,
            distill_status_codes=(200, 204, 400),
        )
        for name, layers in DISTILL_MVT_LAYERS.items()
    ]
