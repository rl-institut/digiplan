"""URLs for map app, including main view and API points."""


from django.conf import settings
from django.urls import path
from django_distill import distill_path
from django_mapengine import mvt
from djgeojson.views import GeoJSONLayerView

from digiplan.map import setup
from digiplan.map.config.config import get_tile_coordinates_for_region

from . import views

app_name = "map"

urlpatterns = [
    path("", views.MapGLView.as_view(), name="map"),
    path("choropleth/<str:lookup>/<str:scenario>", views.get_choropleth, name="choropleth"),
    path("visualization", views.get_visualization, name="visualization"),
    path("popup/<str:lookup>/<int:region>", views.get_popup, name="popup"),
]

urlpatterns += [
    path(f"clusters/{name}.geojson", GeoJSONLayerView.as_view(model=cluster_layer.model))
    for name, cluster_layer in setup.STATIC_LAYERS.items()
]

urlpatterns += [
    path(f"{name}_mvt/<int:z>/<int:x>/<int:y>/", mvt.mvt_view_factory(name, layers))
    for name, layers in setup.MVT_LAYERS.items()
]


def get_all_statics_for_state_lod(view_name: str) -> tuple[int, int, int]:
    """Return distill coordinates for given layer.

    Parameters
    ----------
    view_name: str
        Layer name

    Yields
    ------
    tuple[int, int, int]
        Holding x,y,z
    """
    for x, y, z in get_tile_coordinates_for_region(view_name):
        yield z, x, y


# Distill MVT-urls:
if settings.DISTILL:
    urlpatterns += [
        distill_path(
            f"<int:z>/<int:x>/<int:y>/{name}.mvt",
            mvt.mvt_view_factory(name, layers),
            name=name,
            distill_func=get_all_statics_for_state_lod,
            distill_status_codes=(200, 204, 400),
        )
        for name, layers in setup.DISTILL_MVT_LAYERS.items()
    ]
