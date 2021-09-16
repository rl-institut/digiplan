import json
import os
from dataclasses import dataclass
from itertools import product
from typing import List, Optional

from django.db.models import IntegerField, BooleanField
from raster.models import RasterLayer as RasterModel

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
    # {
    #     "source": "grid",
    #     "color": get_color("grid"),
    #     "model": models.Grid,
    #     "name": "Grids",
    #     "name_singular": "Grid",
    #     "description": "Electricity grids",
    # },
    {
        "source": "nightlight",
        "color": get_color("nightlight"),
        "model": models.Nightlight,
        "name": "Nightlights",
        "name_singular": "Nightlight",
        "description": "See nightlights",
    },
]
HOSPITALS = [
    {
        "source": "built_up_areas",
        "color": get_color("built_up_areas"),
        "model": models.BuiltUpAreas,
        "name": "Built Up Areas",
        "name_singular": "Built Up Area",
        "description": "See cluster",
        "popup_fields": [
            "id",
            "area",
            "population",
            "number_of_hospitals",
            "distance_to_grid",
            "distance_to_light",
            "district_name",
        ],
    },
    {
        "source": "settlements",
        "color": get_color("settlements"),
        "model": models.Settlements,
        "name": "Settlements",
        "name_singular": "Settlement",
        "description": "See cluster",
        "popup_fields": ["id", "area", "population", "number_of_hospitals", "distance_to_grid", "distance_to_light"],
    },
    {
        "source": "hamlets",
        "color": get_color("hamlets"),
        "model": models.Hamlets,
        "name": "Hamlets",
        "name_singular": "Hamlet",
        "description": "See cluster",
        "popup_fields": ["id", "area", "population", "number_of_hospitals"],
    },
    {
        "source": "hospital",
        "color": "red",
        "model": models.Hospitals,
        "name": "Hospitals",
        "name_singular": "Hospital",
        "description": "See nightlights test",
        "popup_fields": [
            "id",
            "name",
            "type",
            "town",
            "ownership",
            "population_per_hospital",
            "catchment_area_hospital",
        ],
    },
    # {
    #     "source": "hospital_simulated",
    #     "color": "red",
    #     "model": models.HospitalsSimulated,
    #     "name": "Simulated Hospitals",
    #     "name_singular": "Simulated hospital",
    #     "description": "See nightlights test",
    #     "popup_fields": [
    #         "id",
    #         "name",
    #         "type",
    #         "town",
    #         "ownership",
    #         "population_per_hospital",
    #         "catchment_area_hospital",
    #     ],
    # },
]
SOLAR = [
    {
        "source": "solar",
        "legend": "solar",
        "model": RasterModel,
        "name": "Solar",
        "name_singular": "Solar",
        "description": "See nightlights test",
    },
]
LAYERS_DEFINITION = ELECTRICITY + HOSPITALS + SOLAR
LAYERS_CATEGORIES = {"Electricty": ELECTRICITY, "Hospitals": HOSPITALS, "Solar": SOLAR}


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


@dataclass
class RasterLayer:
    id: str
    source: str
    type: str


@dataclass
class Popup:
    source: str
    layer_id: str
    fields: str


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


def get_raster_sources(distilled=False):
    sources = []
    for layer in LAYERS_DEFINITION:
        if not issubclass(layer["model"], RasterModel):
            continue
        layer_id = RasterModel.objects.get(name=layer["source"]).id
        sources.append(
            Source(
                name=f"{layer['source']}",
                type="raster",
                tiles=[f"raster/tiles/{layer_id}/{{z}}/{{x}}/{{y}}.png?legend={layer['legend']}"],
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
        + get_raster_sources()
        + get_dynamic_sources()
    )
else:
    SUFFIXES = [""]
    ALL_SOURCES = (
        [Source(name=region, type="vector", tiles=[f"{region}_mvt/{{z}}/{{x}}/{{y}}/"]) for region in REGIONS]
        + [Source(name="static", type="vector", tiles=["static_mvt/{z}/{x}/{y}/"])]
        + get_raster_sources()
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

RASTER_LAYERS = [
    RasterLayer(id=layer["source"], source=layer["source"], type="raster",)
    for layer in LAYERS_DEFINITION
    if issubclass(layer["model"], RasterModel)
]

POPUPS = []
STATIC_LAYERS = []
for layer in LAYERS_DEFINITION:
    if issubclass(layer["model"], RasterModel):
        continue
    if hasattr(layer["model"], "setup"):
        continue
    for suffix in SUFFIXES:
        layer_id = f"fill-{layer['source']}{suffix}"
        STATIC_LAYERS.append(
            Layer(
                id=layer_id,
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
        if "popup_fields" in layer:
            popup_fields = {}
            for field in layer["popup_fields"]:
                label = getattr(layer["model"], field).field.verbose_name if hasattr(layer["model"], field) else field
                popup_fields[label] = field
            POPUPS.append(Popup(layer["source"], layer_id, json.dumps(popup_fields)))

# Sort popups according to prio:
POPUP_PRIO = ["hospital", "hospital_simulated"]  # from high to low prio
POPUPS = sorted(POPUPS, key=lambda x: len(POPUP_PRIO) if x.source not in POPUP_PRIO else POPUP_PRIO.index(x.source))

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
