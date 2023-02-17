from dataclasses import dataclass, field
from itertools import product
from typing import Optional

from django.conf import settings
from django.contrib.gis.db.models import Model
from django.db.models import BooleanField, IntegerField

from digiplan.map.config import config


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


def get_region_layers():
    return (
        [
            MapLayer(
                id=f"line-{layer}",
                type="line",
                source=layer,
                source_layer=layer,
                minzoom=config.ZOOM_LEVELS[layer].min,
                maxzoom=config.ZOOM_LEVELS[layer].max,
                style=config.LAYER_STYLES["region-line"],
            )
            for layer in config.REGIONS
        ]
        + [
            MapLayer(
                id=f"fill-{layer}",
                type="fill",
                source=layer,
                source_layer=layer,
                minzoom=config.ZOOM_LEVELS[layer].min,
                maxzoom=config.ZOOM_LEVELS[layer].max,
                style=config.LAYER_STYLES["region-fill"],
            )
            for layer in config.REGIONS
        ]
        + [
            MapLayer(
                id=f"label-{layer}",
                type="symbol",
                source=layer,
                source_layer=f"{layer}label",
                maxzoom=config.ZOOM_LEVELS[layer].max,
                minzoom=config.ZOOM_LEVELS[layer].min,
                style=config.LAYER_STYLES["region-label"],
            )
            for layer in config.REGIONS
        ]
    )


def get_static_layers(layers):
    suffixes = ["", "_distilled"] if settings.USE_DISTILLED_MVTS else [""]
    static_layers = []
    for layer in layers:
        if hasattr(layer.model, "setup"):
            continue
        for suffix in suffixes:
            if layer.clustered and suffix == "_distilled":
                # Clustered layers are not distilled
                continue
            layer_id = f"{layer.source}{suffix}"
            if layer.clustered:
                min_zoom = list(config.ZOOM_LEVELS.values())[-1].min  # Show unclustered only at last LOD
                max_zoom = config.MAX_ZOOM
            else:
                min_zoom = (
                    config.MAX_DISTILLED_ZOOM + 1 if suffix == "" and settings.USE_DISTILLED_MVTS else config.MIN_ZOOM
                )
                max_zoom = config.MAX_ZOOM if suffix == "" else config.MAX_DISTILLED_ZOOM + 1
            static_layers.append(
                MapLayer(
                    id=layer_id,
                    type="circle",
                    source=f"{layer.map_source}{suffix}",
                    source_layer=layer.source,
                    minzoom=min_zoom,
                    maxzoom=max_zoom,
                    style=config.LAYER_STYLES[layer.source],
                )
            )
    return static_layers


def get_dynamic_layers(layers):
    return [
        MapLayer(
            id=f"fill-{layer.source}-{'-'.join(combination)}",
            type="fill",
            source=f"{layer.source}-{'-'.join(combination)}",
            source_layer=layer.source,
            minzoom=config.MIN_ZOOM,
            maxzoom=config.MAX_ZOOM,
            style=config.LAYER_STYLES[layer.source],
        )
        for layer in layers
        if hasattr(layer.model, "setup")
        for combination in get_layer_setups(layer)
    ]
