import json
import operator
import os
from dataclasses import dataclass, field
from functools import reduce
from itertools import product
from typing import List, Optional

from django.contrib.gis.db.models import Model
from django.db.models import BooleanField, IntegerField
from django.http import HttpRequest

from config.settings.base import APPS_DIR, TILING_SERVICE_TOKEN, USE_DISTILLED_MVTS
from digiplan.map.config.config import (
    LAYER_STYLES,
    MAX_DISTILLED_ZOOM,
    MAX_ZOOM,
    MIN_ZOOM,
    REGIONS,
    ZOOM_LEVELS,
)

from . import models

POPUP_PRIO = ["hospital", "hospital_simulated"]  # from high to low prio


def get_color(source_layer):
    if source_layer not in LAYER_STYLES:
        raise KeyError(f"Could not find layer '{source_layer}' in layer styles (static/config/layer_styles.json)")
    for color_key in ("fill-color", "line-color", "circle-color"):
        try:
            return LAYER_STYLES[source_layer]["paint"][color_key]
        except KeyError:
            continue
    return None


def get_opacity(source_layer):
    return LAYER_STYLES[source_layer]["paint"]["fill-opacity"]


@dataclass
class VectorLayerData:
    # pylint: disable=too-many-instance-attributes
    source: str
    color: str
    model: Model.__class__
    name: str
    description: str
    clustered: bool = False
    map_source: str = "static"
    popup_fields: list = field(default_factory=list)


LAYERS_CATEGORIES = {
    "Renewables": [
        VectorLayerData(
            source="wind",
            color=get_color("wind"),
            model=models.WindTurbine,
            name="Wind Turbines",
            description="Wind Turbines",
        ),
        VectorLayerData(
            source="pvroof",
            color=get_color("pvroof"),
            model=models.PVroof,
            name="roof Photovoltaics",
            description="roof Photovoltaics",
        ),
        VectorLayerData(
            source="pvground",
            color=get_color("pvground"),
            model=models.PVground,
            name="ground Photovoltaics",
            description="ground Photovoltaics",
        ),
        VectorLayerData(
            source="hydro",
            color=get_color("hydro"),
            model=models.Hydro,
            name="Hydro",
            description="",
        ),
        VectorLayerData(
            source="biomass",
            color=get_color("biomass"),
            model=models.Biomass,
            name="Biomass",
            description="",
        ),
        VectorLayerData(
            source="combustion",
            color=get_color("combustion"),
            model=models.Combustion,
            name="Combustion",
            description="",
        ),
    ],
}
LAYERS_DEFINITION = reduce(operator.add, list(LAYERS_CATEGORIES.values()))


@dataclass
class MapSource:
    name: str
    type: str  # noqa: A003
    promote_id: str = "id"
    tiles: Optional[List[str]] = None
    url: Optional[str] = None

    def get_source(self, request: HttpRequest) -> dict:
        """
        Returns source data/tiles using current host and port from request

        Parameters
        ----------
        request: HttpRequest
            Django request holding host and port

        Returns
        -------
        dict
            Containing source data for map
        """
        source = {"type": self.type, "promoteId": self.promote_id}
        if self.type in ("vector", "raster"):
            source["tiles"] = [
                tile if tile.startswith("http") else f"{request.get_raw_uri()}{tile}" for tile in self.tiles
            ]
        else:
            source["data"] = self.url if self.url.startswith("http") else f"{request.get_raw_uri()}{self.url}"
        return source


@dataclass
class MapLayer:
    id: str  # noqa: A003
    type: str  # noqa: A003
    source: str
    style: dict
    source_layer: Optional[str] = None
    minzoom: Optional[int] = None
    maxzoom: Optional[int] = None

    def get_layer(self):
        layer = {"id": self.id, "type": self.type, "source": self.source, **self.style}
        if self.source_layer:
            layer["source-layer"] = self.source_layer
        for attr_name in ("minzoom", "maxzoom"):
            if attr := getattr(self, attr_name):
                layer[attr_name] = attr
        return layer


# pylint: disable=R0903
class MapClusterLayer(MapLayer):
    pass


@dataclass
class Popup:
    source: str
    layer_id: str
    fields: str
    template_url: Optional[str] = None


def get_layer_setups(layer):
    setups = []
    setup_model = layer.model._meta.get_field("setup").related_model
    for setup in setup_model._meta.fields:
        if setup.name == "id":
            continue
        if isinstance(setup, IntegerField):
            setups.append([f"{setup.name}={choice[0]}" for choice in setup.choices])
        elif isinstance(setup, BooleanField):
            setups.append([f"{setup.name}=True", f"{setup.name}=False"])
    return product(*setups)


def get_dynamic_sources():
    sources = []
    for layer in LAYERS_DEFINITION:
        if not hasattr(layer.model, "setup"):
            continue
        for combination in get_layer_setups(layer):
            mvt_str = "-".join(combination)
            filter_str = "&".join(map(lambda x: f"setup__{x}", combination))  # noqa: C417
            sources.append(
                MapSource(
                    name=f"{layer.source}-{mvt_str}",
                    type="vector",
                    tiles=[f"{layer.source}_mvt/{{z}}/{{x}}/{{y}}/?{filter_str}"],
                )
            )
    return sources


if USE_DISTILLED_MVTS:
    SUFFIXES = ["", "_distilled"]
    ALL_SOURCES = (
        [
            MapSource(name=region, type="vector", tiles=[f"{region}_mvt/{{z}}/{{x}}/{{y}}/"])
            for region in REGIONS
            if ZOOM_LEVELS[region].min > MAX_DISTILLED_ZOOM
        ]
        + [
            MapSource(
                name=region,
                type="vector",
                tiles=[f"static/mvts/{{z}}/{{x}}/{{y}}/{region}.mvt"],
            )
            for region in REGIONS
            if ZOOM_LEVELS[region].min < MAX_DISTILLED_ZOOM
        ]
        + [
            MapSource(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"]),
            MapSource(
                name="static_distilled",
                type="vector",
                tiles=["static/mvts/{z}/{x}/{y}/static.mvt"],
            ),
            MapSource(name="results", type="vector", tiles=["results_mvt/{z}/{x}/{y}/"]),
        ]
        + get_dynamic_sources()
    )
else:
    SUFFIXES = [""]
    ALL_SOURCES = (
        [MapSource(name=region, type="vector", tiles=[f"{region}_mvt/{{z}}/{{x}}/{{y}}/"]) for region in REGIONS]
        + [
            MapSource(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"]),
            MapSource(name="results", type="vector", tiles=["results_mvt/{z}/{x}/{y}/"]),
        ]
        + get_dynamic_sources()
    )


ALL_SOURCES += [
    MapSource(
        "satellite",
        type="raster",
        tiles=[f"https://api.maptiler.com/tiles/satellite-v2/{{z}}/{{x}}/{{y}}.jpg?key={TILING_SERVICE_TOKEN}"],
    ),
    MapSource("cluster", type="geojson", url="clusters"),
]


def get_region_layers():
    return (
        [
            MapLayer(
                id=f"line-{layer}",
                type="line",
                source=layer,
                source_layer=layer,
                minzoom=ZOOM_LEVELS[layer].min,
                maxzoom=ZOOM_LEVELS[layer].max,
                style=LAYER_STYLES["region-line"],
            )
            for layer in REGIONS
        ]
        + [
            MapLayer(
                id=f"fill-{layer}",
                type="fill",
                source=layer,
                source_layer=layer,
                minzoom=ZOOM_LEVELS[layer].min,
                maxzoom=ZOOM_LEVELS[layer].max,
                style=LAYER_STYLES["region-fill"],
            )
            for layer in REGIONS
        ]
        + [
            MapLayer(
                id=f"label-{layer}",
                type="symbol",
                source=layer,
                source_layer=f"{layer}label",
                maxzoom=ZOOM_LEVELS[layer].max,
                minzoom=ZOOM_LEVELS[layer].min,
                style=LAYER_STYLES["region-label"],
            )
            for layer in REGIONS
        ]
    )


def get_static_layers():
    static_layers = []
    for layer in LAYERS_DEFINITION:
        if hasattr(layer.model, "setup"):
            continue
        for suffix in SUFFIXES:
            if layer.clustered and suffix == "_distilled":
                # Clustered layers are not distilled
                continue
            layer_id = f"{layer.source}{suffix}"
            if layer.clustered:
                min_zoom = list(ZOOM_LEVELS.values())[-1].min  # Show unclustered only at last LOD
                max_zoom = MAX_ZOOM
            else:
                min_zoom = MAX_DISTILLED_ZOOM + 1 if suffix == "" and USE_DISTILLED_MVTS else MIN_ZOOM
                max_zoom = MAX_ZOOM if suffix == "" else MAX_DISTILLED_ZOOM + 1
            static_layers.append(
                MapLayer(
                    id=layer_id,
                    type="circle",
                    source=f"{layer.map_source}{suffix}",
                    source_layer=layer.source,
                    minzoom=min_zoom,
                    maxzoom=max_zoom,
                    style=LAYER_STYLES[layer.source],
                )
            )
    return static_layers


def get_dynamic_layers():
    return [
        MapLayer(
            id=f"fill-{layer.source}-{'-'.join(combination)}",
            type="fill",
            source=f"{layer.source}-{'-'.join(combination)}",
            source_layer=layer.source,
            minzoom=MIN_ZOOM,
            maxzoom=MAX_ZOOM,
            style=LAYER_STYLES[layer.source],
        )
        for layer in LAYERS_DEFINITION
        if hasattr(layer.model, "setup")
        for combination in get_layer_setups(layer)
    ]


def get_popups():
    popups = []
    for layer in LAYERS_DEFINITION:
        if not layer.popup_fields:
            continue

        for suffix in SUFFIXES:
            if layer.clustered and suffix == "_distilled":
                # Clustered layers are not distilled
                continue
            layer_id = f"{layer.source}{suffix}"

            popup_fields = {}
            for popup_field in layer.popup_fields:
                label = (
                    getattr(layer.model, popup_field).field.verbose_name
                    if hasattr(layer.model, popup_field)
                    else popup_field
                )
                popup_fields[label] = popup_field
            template_url = (
                f"popups/{layer.source}.html"
                if os.path.exists(APPS_DIR.path("templates", "popups", f"{layer.source}.html"))
                else None
            )
            popups.append(Popup(layer.source, layer_id, json.dumps(popup_fields), template_url=template_url))
    return sorted(popups, key=lambda x: len(POPUP_PRIO) if x.source not in POPUP_PRIO else POPUP_PRIO.index(x.source))


STATIC_LAYERS = get_static_layers()
DYNAMIC_LAYERS = get_dynamic_layers()
REGION_LAYERS = get_region_layers()

ALL_LAYERS = STATIC_LAYERS + DYNAMIC_LAYERS + REGION_LAYERS
ALL_LAYERS.append(
    MapLayer(id="results", type="fill", source="results", source_layer="results", style=LAYER_STYLES["results"])
)
# pylint:disable=W0511
# FIXME: Build results layer before!

POPUPS = get_popups()
