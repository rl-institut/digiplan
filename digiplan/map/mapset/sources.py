from dataclasses import dataclass
from typing import List, Optional

from django.http import HttpRequest

from digiplan.map.mapset import utils


@dataclass
class MapSource:
    name: str
    type: str  # noqa: A003
    promote_id: str = "id"
    tiles: Optional[List[str]] = None
    url: Optional[str] = None
    minzoom: Optional[int] = None
    maxzoom: Optional[int] = None

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
        if self.minzoom:
            source["minzoom"] = self.minzoom
        if self.maxzoom:
            source["maxzoom"] = self.maxzoom
        if self.type in ("vector", "raster"):
            source["tiles"] = [
                tile if tile.startswith("http") else f"{request.get_raw_uri()}{tile}" for tile in self.tiles
            ]
        else:
            source["data"] = self.url if self.url.startswith("http") else f"{request.get_raw_uri()}{self.url}"
        return source


def get_dynamic_sources(layers):
    sources = []
    for layer in layers:
        if not hasattr(layer.model, "setup"):
            continue
        for combination in utils.get_layer_setups(layer):
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
