import os
import json
from dataclasses import dataclass, field
from itertools import product
from typing import List, Optional

from django.contrib.gis.db.models import Model
from django.db.models import IntegerField, BooleanField, ObjectDoesNotExist
from raster.models import RasterLayer as RasterModel

from config.settings.base import APPS_DIR, USE_DISTILLED_MVTS
from .config import LAYER_STYLES, MAX_ZOOM, MIN_ZOOM, REGIONS, ZOOM_LEVELS, MAX_DISTILLED_ZOOM

from . import models


def get_color(source_layer):
    return LAYER_STYLES[source_layer]["paint"]["fill-color"]


def get_opacity(source_layer):
    return LAYER_STYLES[source_layer]["paint"]["fill-opacity"]


@dataclass
class VectorLayerData:
    source: str
    color: str
    model: Model.__class__
    name: str
    name_singular: str
    description: str
    clustered: bool = False
    popup_fields: list = field(default_factory=list)


@dataclass
class RasterLayerData:
    source: str
    filepath: str
    legend: str
    model: RasterModel.__class__
    name: str
    name_singular: str
    description: str


ELECTRICITY: list = [
    VectorLayerData(
        source="nightlight",
        color=get_color("nightlight"),
        model=models.Nightlight,
        name="Nightlights",
        name_singular="Nightlight",
        description="See nightlights",
    )
]

HOSPITALS: list = [
    VectorLayerData(
        source="built_up_areas",
        color=get_color("built_up_areas"),
        model=models.BuiltUpAreas,
        name="Built Up Areas",
        name_singular="Built Up Area",
        description="See cluster",
        popup_fields=[
            "id",
            "area",
            "population",
            "number_of_hospitals",
            "distance_to_grid",
            "distance_to_light",
            "district_name",
        ],
    ),
    VectorLayerData(
        source="settlements",
        color=get_color("settlements"),
        model=models.Settlements,
        name="Settlements",
        name_singular="Settlement",
        description="See cluster",
        popup_fields=["id", "area", "population", "number_of_hospitals", "distance_to_grid", "distance_to_light"],
    ),
    VectorLayerData(
        source="hamlets",
        color=get_color("hamlets"),
        model=models.Hamlets,
        name="Hamlets",
        name_singular="Hamlet",
        description="See cluster",
        clustered=True,
        popup_fields=["id", "area", "population", "number_of_hospitals"],
    ),
    VectorLayerData(
        source="hospital",
        color="red",
        model=models.Hospitals,
        name="Hospitals",
        name_singular="Hospital",
        description="See nightlights test",
        popup_fields=["id", "name", "type", "town", "ownership", "population_per_hospital", "catchment_area_hospital"],
    ),
    # VectorLayerData(
    #     source="hospital_simulated",
    #     color="red",
    #     model=models.HospitalsSimulated,
    #     name="Simulated Hospitals",
    #     name_singular="Simulated hospital",
    #     description="See nightlights test",
    #     popup_fields=[
    #         "id",
    #         "name",
    #         "type",
    #         "town",
    #         "ownership",
    #         "population_per_hospital",
    #         "catchment_area_hospital",
    #     ],
    # ),
]
SOLAR: list = [
    RasterLayerData(
        source="solar",
        filepath="Gha_Yearly_Solar_horizontal_irradiation.tif",
        legend="solar",
        model=RasterModel,
        name="Solar",
        name_singular="Solar",
        description="See nightlights test",
    ),
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
    clustered: bool = False


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
    template_url: Optional[str] = None


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
        if not hasattr(layer.model, "setup"):
            continue
        for combination in get_layer_setups(layer):
            mvt_str = "-".join(combination)
            filter_str = "&".join(map(lambda x: f"setup__{x}", combination))
            sources.append(
                Source(
                    name=f"{layer.source}-{mvt_str}",
                    type="vector",
                    tiles=[f"{layer.source}_mvt/{{z}}/{{x}}/{{y}}/?{filter_str}"],
                )
            )
    return sources


def get_raster_sources(distilled=False):
    sources = []
    for layer in LAYERS_DEFINITION:
        if not issubclass(layer.model, RasterModel):
            continue
        try:
            raster_id = RasterModel.objects.get(name=layer.source).id
        except ObjectDoesNotExist:
            continue
        sources.append(
            Source(
                name=f"{layer.source}",
                type="raster",
                tiles=[f"raster/tiles/{raster_id}/{{z}}/{{x}}/{{y}}.png?legend={layer.legend}"],
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
    RasterLayer(id=layer.source, source=layer.source, type="raster",)
    for layer in LAYERS_DEFINITION
    if issubclass(layer.model, RasterModel)
]

POPUPS = []
STATIC_LAYERS = []
for layer in LAYERS_DEFINITION:
    if issubclass(layer.model, RasterModel):
        continue
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
        STATIC_LAYERS.append(
            Layer(
                id=layer_id,
                color=layer.color,
                description=layer.description,
                minzoom=min_zoom,
                maxzoom=max_zoom,
                name=layer.name,
                style=layer.source,
                source=f"static{suffix}",
                source_layer=layer.source,
                type="static",
                clustered=layer.clustered,
            )
        )
        if layer.popup_fields:
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
            POPUPS.append(Popup(layer.source, layer_id, json.dumps(popup_fields), template_url=template_url))

# Sort popups according to prio:
POPUP_PRIO = ["hospital", "hospital_simulated"]  # from high to low prio
POPUPS = sorted(POPUPS, key=lambda x: len(POPUP_PRIO) if x.source not in POPUP_PRIO else POPUP_PRIO.index(x.source))

DYNAMIC_LAYERS = [
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

ALL_LAYERS = STATIC_LAYERS + DYNAMIC_LAYERS + REGION_LAYERS
