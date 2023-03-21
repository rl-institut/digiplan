"""Actual map setup is done here."""

from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django_mapengine import layers, sources, utils

from digiplan.map import models

STATIC_LAYERS = {
    "wind": layers.ClusterModelLayer(id="wind", model=models.WindTurbine, source="wind"),
    "pvroof": layers.StaticModelLayer(id="pvroof", model=models.PVroof, source="static"),
    "pvground": layers.StaticModelLayer(id="pvground", model=models.PVground, source="static"),
    "hydro": layers.StaticModelLayer(id="hydro", model=models.Hydro, source="static"),
    "biomass": layers.StaticModelLayer(id="biomass", model=models.Biomass, source="static"),
    "combustion": layers.StaticModelLayer(id="combustion", model=models.Combustion, source="static"),
}


@dataclass
class LegendLayer:
    """Define a legend item with color which can activate a layer from model in map."""

    name: str
    description: str
    layer: layers.ModelLayer
    color: Optional[str] = None

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
        return utils.get_color(self.layer.id)


LEGEND = {
    "Renewables": [
        LegendLayer("Windturbinen", "", STATIC_LAYERS["wind"]),
        LegendLayer("Aufdach-PV", "", STATIC_LAYERS["pvroof"]),
        LegendLayer("Boden-PV", "", STATIC_LAYERS["pvground"]),
        LegendLayer("Hydro", "", STATIC_LAYERS["hydro"]),
        LegendLayer("Biomasse", "", STATIC_LAYERS["biomass"]),
        LegendLayer("Fossile Kraftwerke", "", STATIC_LAYERS["combustion"]),
    ],
}

REGION_LAYERS = list(layers.get_region_layers())
RESULT_LAYERS = [
    layers.MapLayer(
        id="results",
        source="results",
        source_layer="results",
        style=settings.MAP_ENGINE_LAYER_STYLES["results"],
    ),
]

# Order is important! Last items are shown on top!
ALL_LAYERS = REGION_LAYERS + RESULT_LAYERS
for static_layer in STATIC_LAYERS.values():
    ALL_LAYERS.extend(static_layer.get_map_layers())

LAYERS_AT_STARTUP = [layer.id for layer in REGION_LAYERS]

if settings.MAP_ENGINE_USE_DISTILLED_MVTS:
    SOURCES = [
        sources.MapSource(name=region, type="vector", tiles=[f"map/{region}_mvt/{{z}}/{{x}}/{{y}}/"])
        for region in settings.MAP_ENGINE_REGIONS
        if settings.MAP_ENGINE_ZOOM_LEVELS[region].min > settings.MAP_ENGINE_MAX_DISTILLED_ZOOM
    ] + [
        sources.MapSource(
            name=region,
            type="vector",
            tiles=[f"static/mvts/{{z}}/{{x}}/{{y}}/{region}.mvt"],
            maxzoom=settings.MAP_ENGINE_MAX_DISTILLED_ZOOM + 1,
        )
        for region in settings.MAP_ENGINE_REGIONS
        if settings.MAP_ENGINE_ZOOM_LEVELS[region].min < settings.MAP_ENGINE_MAX_DISTILLED_ZOOM
    ]
else:
    SOURCES = [
        sources.MapSource(name=region, type="vector", tiles=[f"map/{region}_mvt/{{z}}/{{x}}/{{y}}/"])
        for region in settings.MAP_ENGINE_REGIONS
    ]

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
    sources.MapSource(name="static", type="vector", tiles=["map/static_mvt/{z}/{x}/{y}/"]),
    sources.MapSource(name="static_distilled", type="vector", tiles=["map/static/mvts/{z}/{x}/{y}/static.mvt"]),
    sources.MapSource(name="results", type="vector", tiles=["map/results_mvt/{z}/{x}/{y}/"]),
]
