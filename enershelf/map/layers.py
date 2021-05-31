import json
import os
from dataclasses import dataclass
from itertools import product
from typing import List, Optional

from django.db.models import IntegerField, BooleanField

from config.settings.base import USE_DISTILLED_MVTS
from .config import MAX_ZOOM, MIN_ZOOM, REGIONS, ZOOM_LEVELS, MAX_DISTILLED_ZOOM

from . import models

with open(os.path.join(os.path.dirname(__file__), "../static/styles/layer_styles.json"), mode="rb",) as f:
    LAYER_STYLES = json.loads(f.read())


def get_color(source_layer):
    return LAYER_STYLES[source_layer]["paint"]["fill-color"]


def get_opacity(source_layer):
    return LAYER_STYLES[source_layer]["paint"]["fill-opacity"]


ELECTRICITY = [
    {
        "source": "grid",
        "color": get_color("grid"),
        "model": models.Grid,
        "name": "Grids",
        "name_singular": "Grid",
        "description": "Electricity grids",
    },
]
LAYERS_DEFINITION = ELECTRICITY
LAYERS_CATEGORIES = {
    "Electricty": ELECTRICITY,
}


@dataclass
class Source:
    name: str
    type: str
    tiles: Optional[List[str]] = None
    url: Optional[str] = None


@dataclass
class Layer:
    id: str
    minzoom: int
    maxzoom: int
    style: str
    source: str
    source_layer: str
    type: str
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


def get_layer_setups(layer):
    setups = []
    setup_model = layer["model"]._meta.get_field("setup").related_model
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
        if not hasattr(layer["model"], "setup"):
            continue
        for combination in get_layer_setups(layer):
            mvt_str = "-".join(combination)
            filter_str = "&".join(map(lambda x: f"setup__{x}", combination))
            sources.append(
                Source(
                    name=f"{layer['source']}-{mvt_str}",
                    type="vector",
                    tiles=[f"{layer['source']}_mvt/{{z}}/{{x}}/{{y}}/?{filter_str}"],
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
            Source(name=region, type="vector", tiles=[f"static/mvts/{{z}}/{{x}}/{{y}}/{region}.mvt"],)
            for region in REGIONS
            if ZOOM_LEVELS[region].min < MAX_DISTILLED_ZOOM
        ]
        + [
            Source(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"]),
            Source(name="static_distilled", type="vector", tiles=["static/mvts/{z}/{x}/{y}/static.mvt"],),
        ]
        + get_dynamic_sources()
    )
else:
    SUFFIXES = [""]
    ALL_SOURCES = (
        [Source(name=region, type="vector", tiles=[f"{region}_mvt/{{z}}/{{x}}/{{y}}/"]) for region in REGIONS]
        + [Source(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"])]
        + get_dynamic_sources()
    )

REGION_LAYERS = (
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

STATIC_LAYERS = []
for layer in LAYERS_DEFINITION:
    if hasattr(layer["model"], "setup"):
        continue
    for suffix in SUFFIXES:
        STATIC_LAYERS.append(
            Layer(
                id=f"fill-{layer['source']}{suffix}",
                color=layer["color"],
                description=layer["description"],
                minzoom=MAX_DISTILLED_ZOOM + 1 if suffix == "" and USE_DISTILLED_MVTS else MIN_ZOOM,
                maxzoom=MAX_ZOOM if suffix == "" else MAX_DISTILLED_ZOOM + 1,
                name=layer["name"],
                style=layer["source"],
                source=f"static{suffix}",
                source_layer=layer["source"],
                type="static",
            )
        )

DYNAMIC_LAYERS = [
    Layer(
        id=f"fill-{layer['source']}-{'-'.join(combination)}",
        color=layer["color"],
        description=layer["description"],
        minzoom=MIN_ZOOM,
        maxzoom=MAX_ZOOM,
        name=layer["name"],
        style=layer["source"],
        source=f"{layer['source']}-{'-'.join(combination)}",
        source_layer=layer["source"],
        type="static",
    )
    for layer in LAYERS_DEFINITION
    if hasattr(layer["model"], "setup")
    for combination in get_layer_setups(layer)
]

ALL_LAYERS = STATIC_LAYERS + DYNAMIC_LAYERS + REGION_LAYERS
