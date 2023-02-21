from dataclasses import dataclass
from typing import Optional

from django.conf import settings

from digiplan.map import models
from digiplan.map.config import config
from digiplan.map.mapset import layers, popups, sources, utils

STATIC_LAYERS = {
    "wind": layers.StaticLayer(id="wind", model=models.WindTurbine, type="circle", source="static"),
    "pvroof": layers.StaticLayer(id="pvroof", model=models.PVroof, type="circle", source="static"),
    "pvground": layers.StaticLayer(id="pvground", model=models.PVground, type="circle", source="static"),
    "hydro": layers.StaticLayer(id="hydro", model=models.Hydro, type="circle", source="static"),
    "biomass": layers.StaticLayer(id="biomass", model=models.Biomass, type="circle", source="static"),
    "combustion": layers.StaticLayer(id="combustion", model=models.Combustion, type="circle", source="static"),
}


@dataclass
class LegendLayer:
    name: str
    description: str
    layer: layers.StaticLayer
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

ALL_LAYERS = []
for static_layer in STATIC_LAYERS.values():
    ALL_LAYERS.extend(static_layer.get_map_layers())
ALL_LAYERS += DYNAMIC_LAYERS + REGION_LAYERS
ALL_LAYERS.append(
    layers.MapLayer(
        id="results", type="fill", source="results", source_layer="results", style=config.LAYER_STYLES["results"]
    )
)
# pylint:disable=W0511
# FIXME: Build results layer before!

LAYERS_AT_STARTUP = [layer.id for layer in REGION_LAYERS]

POPUP_PRIO = ["hospital", "hospital_simulated"]  # from high to low prio
POPUPS = popups.get_popups(LAYERS_DEFINITION, POPUP_PRIO)

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
    sources.MapSource("cluster", type="geojson", url="clusters"),
    sources.MapSource(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"]),
    sources.MapSource(
        name="static_distilled",
        type="vector",
        tiles=["static/mvts/{z}/{x}/{y}/static.mvt"],
    ),
    sources.MapSource(name="results", type="vector", tiles=["results_mvt/{z}/{x}/{y}/"]),
] + sources.get_dynamic_sources(LAYERS_DEFINITION)