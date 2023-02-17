from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.contrib.gis.db.models import Model

from digiplan.map.config import config
from digiplan.map.mapset import utils


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


@dataclass
class StaticLayer:
    id: str  # noqa: A003
    model: Model.__class__
    type: str  # noqa: A003
    source: str

    @staticmethod
    def min_zoom(distill=False):
        return config.MAX_DISTILLED_ZOOM + 1 if not distill and settings.USE_DISTILLED_MVTS else config.MIN_ZOOM

    @staticmethod
    def max_zoom(distill=False):
        return config.MAX_ZOOM if not distill else config.MAX_DISTILLED_ZOOM + 1

    def get_map_layers(self):
        yield MapLayer(
            id=self.id,
            type=self.type,
            source=self.source,
            source_layer=self.id,
            minzoom=self.min_zoom(),
            maxzoom=self.max_zoom(),
            style=config.LAYER_STYLES[self.id],
        )
        if settings.USE_DISTILLED_MVTS:
            yield MapLayer(
                id=f"{self.id}_distilled",
                type=self.type,
                source=f"{self.source}_distilled",
                source_layer=self.id,
                minzoom=self.min_zoom(),
                maxzoom=self.max_zoom(),
                style=config.LAYER_STYLES[self.id],
            )


# pylint: disable=R0903
class MapClusterLayer(MapLayer):
    pass


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
        for combination in utils.get_layer_setups(layer)
    ]
