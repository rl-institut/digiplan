"""Actual map setup is done here."""

from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django_mapengine import layers, sources, utils


@dataclass
class LegendLayer:
    """Define a legend item with color which can activate a layer from model in map."""

    name: str
    description: str
    layer: layers.ModelLayer = None
    layer_id: str = None
    color: Optional[str] = None

    def __post_init__(self):
        if self.layer is None and self.layer_id is None:
            raise ValueError("You must either set layer or layer_id.")

    def get_color(self) -> str:
        """
        Return color to show on legend. If color is not set, color is tried to be read from layer style.

        Returns
        -------
        str
            Color string (name/rgb/hex/etc.) to be used on legend in frontend.
        """
        if self.color:
            return self.color
        return utils.get_color(self.get_layer_id())

    def get_layer_id(self):
        if self.layer_id:
            return self.layer_id
        return self.layer.id

    @property
    def model(self):
        if self.layer:
            return self.layer.model
        return layers.get_layer_by_id(self.get_layer_id()).model


LEGEND = {
    "Renewables": [
        LegendLayer("Windturbinen", "", layer_id="wind", color="blue"),
        LegendLayer("Aufdach-PV", "", layer_id="pvroof", color="yellow"),
        LegendLayer("Boden-PV", "", layer_id="pvground"),
        LegendLayer("Hydro", "", layer_id="hydro"),
        LegendLayer("Biomasse", "", layer_id="biomass"),
        LegendLayer("Fossile Kraftwerke", "", layer_id="combustion"),
    ],
}

REGION_LAYERS = list(layers.get_region_layers())

# Order is important! Last items are shown on top!
ALL_LAYERS = REGION_LAYERS
for cluster_layer in layers.get_cluster_layers():
    ALL_LAYERS.extend(cluster_layer.get_map_layers())
for static_layer in layers.get_static_layers():
    ALL_LAYERS.extend(static_layer.get_map_layers())


SOURCES = list(sources.get_region_sources())

SOURCES += [
    sources.MapSource(
        "satellite",
        type="raster",
        tiles=[
            "https://api.maptiler.com/tiles/satellite-v2/"
            f"{{z}}/{{x}}/{{y}}.jpg?key={settings.MAP_ENGINE_TILING_SERVICE_TOKEN}",
        ],
    ),
    sources.ClusterMapSource("wind", type="geojson", url="map/clusters/wind.geojson"),
    sources.ClusterMapSource("pvroof", type="geojson", url="map/clusters/pvroof.geojson"),
    sources.MapSource(name="static", type="vector", tiles=["map/static_mvt/{z}/{x}/{y}/"]),
    sources.MapSource(name="static_distilled", type="vector", tiles=["map/static/mvts/{z}/{x}/{y}/static.mvt"]),
    sources.MapSource(name="results", type="vector", tiles=["map/results_mvt/{z}/{x}/{y}/"]),
]
