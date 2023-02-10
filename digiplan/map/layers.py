import json
import operator
import os
from dataclasses import dataclass, field
from functools import reduce
from itertools import product
from typing import List, Optional

from django.contrib.gis.db.models import Model
from django.db.models import BooleanField, IntegerField

from config.settings.base import APPS_DIR, USE_DISTILLED_MVTS
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
    try:
        return LAYER_STYLES[source_layer]["paint"]["fill-color"]
    except KeyError:
        return LAYER_STYLES[source_layer]["paint"]["line-color"]


def get_opacity(source_layer):
    return LAYER_STYLES[source_layer]["paint"]["fill-opacity"]


@dataclass
class VectorLayerData:
    # pylint: disable=too-many-instance-attributes
    source: str
    color: str
    model: Model.__class__
    name: str
    name_singular: str
    description: str
    clustered: bool = False
    map_source: str = "static"
    popup_fields: list = field(default_factory=list)


LAYERS_CATEGORIES = {
    "Renewables": [
        VectorLayerData(
            source="wind",
            color="blue",
            model=models.WindTurbine,
            name="Wind Turbines",
            name_singular="Wind Turbine",
            description="Wind Turbines",
        ),
        VectorLayerData(
            source="pvroof",
            color="blue",
            model=models.PVroof,
            name="roof Photovoltaics",
            name_singular="roof Photovoltaic",
            description="roof Photovoltaics",
        ),
        VectorLayerData(
            source="pvground",
            color="blue",
            model=models.PVground,
            name="ground Photovoltaics",
            name_singular="ground Photovoltaic",
            description="ground Photovoltaics",
        ),
        VectorLayerData(
            source="hydro",
            color="blue",
            model=models.Hydro,
            name="Hydro",
            name_singular="Hydro",
            description="",
        ),
        VectorLayerData(
            source="biomass",
            color="blue",
            model=models.Biomass,
            name="Biomass",
            name_singular="Biomass",
            description="",
        ),
        VectorLayerData(
            source="combustion",
            color="blue",
            model=models.Combustion,
            name="Combustion",
            name_singular="Combustion",
            description="",
        ),
    ],
    "Results": [
        VectorLayerData(
            source="results",
            map_source="results",
            color=get_color("results"),
            model=models.Municipality,
            name="Ergebnisse",
            name_singular="Ergebnis",
            description="",
            popup_fields=("title", "municipality", "key-values", "chart", "description", "sources"),
            # order matters
        )
    ],
}
LAYERS_DEFINITION = reduce(operator.add, list(LAYERS_CATEGORIES.values()))


@dataclass
class Source:
    name: str
    type: str  # noqa: A003
    tiles: Optional[List[str]] = None
    url: Optional[str] = None


@dataclass
class Layer:
    # pylint: disable=too-many-instance-attributes
    id: str  # noqa: A003
    minzoom: int
    maxzoom: int
    style: str
    source: str
    source_layer: str
    type: str  # noqa: A003
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    clustered: bool = False


@dataclass
class RasterLayer:
    id: str  # noqa: A003
    source: str
    type: str  # noqa: A003


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
                Source(
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
            Source(name=region, type="vector", tiles=[f"{region}_mvt/{{z}}/{{x}}/{{y}}/"])
            for region in REGIONS
            if ZOOM_LEVELS[region].min > MAX_DISTILLED_ZOOM
        ]
        + [
            Source(
                name=region,
                type="vector",
                tiles=[f"static/mvts/{{z}}/{{x}}/{{y}}/{region}.mvt"],
            )
            for region in REGIONS
            if ZOOM_LEVELS[region].min < MAX_DISTILLED_ZOOM
        ]
        + [
            Source(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"]),
            Source(
                name="static_distilled",
                type="vector",
                tiles=["static/mvts/{z}/{x}/{y}/static.mvt"],
            ),
            Source(name="results", type="vector", tiles=["results_mvt/{z}/{x}/{y}/"]),
        ]
        + get_dynamic_sources()
    )
else:
    SUFFIXES = [""]
    ALL_SOURCES = (
        [Source(name=region, type="vector", tiles=[f"{region}_mvt/{{z}}/{{x}}/{{y}}/"]) for region in REGIONS]
        + [
            Source(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"]),
            Source(name="results", type="vector", tiles=["results_mvt/{z}/{x}/{y}/"]),
        ]
        + get_dynamic_sources()
    )


def get_region_layers():
    return (
        [
            Layer(
                id=f"line-{layer}",
                minzoom=ZOOM_LEVELS[layer].min,
                maxzoom=ZOOM_LEVELS[layer].max,
                style="region-line",
                source=layer,
                source_layer=layer,
                type="region",
            )
            for layer in REGIONS
        ]
        + [
            Layer(
                id=f"fill-{layer}",
                minzoom=ZOOM_LEVELS[layer].min,
                maxzoom=ZOOM_LEVELS[layer].max,
                style="region-fill",
                source=layer,
                source_layer=layer,
                type="region",
            )
            for layer in REGIONS
        ]
        + [
            Layer(
                id=f"label-{layer}",
                maxzoom=ZOOM_LEVELS[layer].max,
                minzoom=ZOOM_LEVELS[layer].min,
                style="region-label",
                source=layer,
                source_layer=f"{layer}label",
                type="region",
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
                Layer(
                    id=layer_id,
                    color=layer.color,
                    description=layer.description,
                    minzoom=min_zoom,
                    maxzoom=max_zoom,
                    name=layer.name,
                    style=layer.source,
                    source=f"{layer.map_source}{suffix}",
                    source_layer=layer.source,
                    type="static",
                    clustered=layer.clustered,
                )
            )
    return static_layers


def get_dynamic_layers():
    return [
        Layer(
            id=f"fill-{layer.source}-{'-'.join(combination)}",
            color=layer.color,
            description=layer.description,
            minzoom=MIN_ZOOM,
            maxzoom=MAX_ZOOM,
            name=layer.name,
            style=layer.source,
            source=f"{layer.source}-{'-'.join(combination)}",
            source_layer=layer.source,
            type="static",
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

POPUPS = get_popups()
