import operator
from functools import reduce

from django.conf import settings

from digiplan.map import models
from digiplan.map.config import config
from digiplan.map.mapset import layers, popups, sources, utils

LAYERS_CATEGORIES = {
    "Renewables": [
        layers.VectorLayerData(
            source="wind",
            color=utils.get_color("wind"),
            model=models.WindTurbine,
            name="Wind Turbines",
            description="Wind Turbines",
        ),
        layers.VectorLayerData(
            source="pvroof",
            color=utils.get_color("pvroof"),
            model=models.PVroof,
            name="roof Photovoltaics",
            description="roof Photovoltaics",
        ),
        layers.VectorLayerData(
            source="pvground",
            color=utils.get_color("pvground"),
            model=models.PVground,
            name="ground Photovoltaics",
            description="ground Photovoltaics",
        ),
        layers.VectorLayerData(
            source="hydro",
            color=utils.get_color("hydro"),
            model=models.Hydro,
            name="Hydro",
            description="",
        ),
        layers.VectorLayerData(
            source="biomass",
            color=utils.get_color("biomass"),
            model=models.Biomass,
            name="Biomass",
            description="",
        ),
        layers.VectorLayerData(
            source="combustion",
            color=utils.get_color("combustion"),
            model=models.Combustion,
            name="Combustion",
            description="",
        ),
    ],
}
LAYERS_DEFINITION = reduce(operator.add, list(LAYERS_CATEGORIES.values()))

if settings.USE_DISTILLED_MVTS:
    SUFFIXES = ["", "_distilled"]
    ALL_SOURCES = (
        [
            sources.MapSource(name=region, type="vector", tiles=[f"{region}_mvt/{{z}}/{{x}}/{{y}}/"])
            for region in config.REGIONS
            if config.ZOOM_LEVELS[region].min > config.MAX_DISTILLED_ZOOM
        ]
        + [
            sources.MapSource(
                name=region,
                type="vector",
                tiles=[f"static/mvts/{{z}}/{{x}}/{{y}}/{region}.mvt"],
            )
            for region in config.REGIONS
            if config.ZOOM_LEVELS[region].min < config.MAX_DISTILLED_ZOOM
        ]
        + [
            sources.MapSource(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"]),
            sources.MapSource(
                name="static_distilled",
                type="vector",
                tiles=["static/mvts/{z}/{x}/{y}/static.mvt"],
            ),
            sources.MapSource(name="results", type="vector", tiles=["results_mvt/{z}/{x}/{y}/"]),
        ]
        + sources.get_dynamic_sources(LAYERS_DEFINITION)
    )
else:
    SUFFIXES = [""]
    ALL_SOURCES = (
        [
            sources.MapSource(name=region, type="vector", tiles=[f"{region}_mvt/{{z}}/{{x}}/{{y}}/"])
            for region in config.REGIONS
        ]
        + [
            sources.MapSource(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"]),
            sources.MapSource(name="results", type="vector", tiles=["results_mvt/{z}/{x}/{y}/"]),
        ]
        + sources.get_dynamic_sources(LAYERS_DEFINITION)
    )


ALL_SOURCES += [
    sources.MapSource(
        "satellite",
        type="raster",
        tiles=[
            f"https://api.maptiler.com/tiles/satellite-v2/{{z}}/{{x}}/{{y}}.jpg?key={settings.TILING_SERVICE_TOKEN}"
        ],
    ),
    sources.MapSource("cluster", type="geojson", url="clusters"),
]


STATIC_LAYERS = layers.get_static_layers(LAYERS_DEFINITION)
DYNAMIC_LAYERS = layers.get_dynamic_layers(LAYERS_DEFINITION)
REGION_LAYERS = layers.get_region_layers()

ALL_LAYERS = STATIC_LAYERS + DYNAMIC_LAYERS + REGION_LAYERS
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
