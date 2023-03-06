from dataclasses import dataclass
from typing import Optional

from django.conf import settings

from digiplan.map import models
from digiplan.map.config import config
from digiplan.map.mapset import layers, sources, utils

STATIC_LAYERS = {
    "wind": layers.ClusterModelLayer(id="wind", model=models.WindTurbine, type="circle", source="static"),
    "pvroof": layers.StaticModelLayer(id="pvroof", model=models.PVroof, type="circle", source="static"),
    "pvground": layers.StaticModelLayer(id="pvground", model=models.PVground, type="circle", source="static"),
    "hydro": layers.StaticModelLayer(id="hydro", model=models.Hydro, type="circle", source="static"),
    "biomass": layers.StaticModelLayer(id="biomass", model=models.Biomass, type="circle", source="static"),
    "combustion": layers.StaticModelLayer(id="combustion", model=models.Combustion, type="circle", source="static"),
}


@dataclass
class LegendLayer:
    name: str
    description: str
    layer: layers.ModelLayer
    color: Optional[str] = None

    def get_color(self):
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
LAYERS_DEFINITION = []

DYNAMIC_LAYERS = layers.get_dynamic_layers(LAYERS_DEFINITION)
REGION_LAYERS = layers.get_region_layers()
RESULT_LAYERS = [
    layers.MapLayer(
        id="results",
        type="fill",
        source="results",
        source_layer="results",
        style=config.LAYER_STYLES["results"],
    ),
]


# Order is important! Last items are shown on top!
ALL_LAYERS = REGION_LAYERS + RESULT_LAYERS + DYNAMIC_LAYERS
for static_layer in STATIC_LAYERS.values():
    ALL_LAYERS.extend(static_layer.get_map_layers())

LAYERS_AT_STARTUP = [layer.id for layer in REGION_LAYERS]

POPUPS = ["results"]

if settings.USE_DISTILLED_MVTS:
    SOURCES = [
        sources.MapSource(name=region, type="vector", tiles=[f"{region}_mvt/{{z}}/{{x}}/{{y}}/"])
        for region in config.REGIONS
        if config.ZOOM_LEVELS[region].min > config.MAX_DISTILLED_ZOOM
    ] + [
        sources.MapSource(
            name=region,
            type="vector",
            tiles=[f"static/mvts/{{z}}/{{x}}/{{y}}/{region}.mvt"],
            maxzoom=config.MAX_DISTILLED_ZOOM + 1,
        )
        for region in config.REGIONS
        if config.ZOOM_LEVELS[region].min < config.MAX_DISTILLED_ZOOM
    ]
else:
    SOURCES = [
        sources.MapSource(name=region, type="vector", tiles=[f"{region}_mvt/{{z}}/{{x}}/{{y}}/"])
        for region in config.REGIONS
    ]

SOURCES += [
    sources.MapSource(
        "satellite",
        type="raster",
        tiles=[
            f"https://api.maptiler.com/tiles/satellite-v2/{{z}}/{{x}}/{{y}}.jpg?key={settings.TILING_SERVICE_TOKEN}"
        ],
    ),
    sources.MapSource("wind", type="geojson", url="clusters/wind.geojson", cluster=True),
    sources.MapSource(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"]),
    sources.MapSource(name="static_distilled", type="vector", tiles=["static/mvts/{z}/{x}/{y}/static.mvt"]),
    sources.MapSource(name="results", type="vector", tiles=["results_mvt/{z}/{x}/{y}/"]),
    *sources.get_dynamic_sources(LAYERS_DEFINITION),
]
