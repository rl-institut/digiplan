"""Actual map setup is done here."""

from dataclasses import dataclass
from typing import Optional

from django_mapengine import layers, utils


@dataclass
class LegendLayer:
    """Define a legend item with color which can activate a layer from model in map."""

    name: str
    description: str
    layer: layers.ModelLayer = None
    layer_id: str = None
    color: Optional[str] = None

    def __post_init__(self):
        if self.layer is None and self.layer_id is None:
            raise ValueError("You must either set layer or layer_id.")

    def get_color(self) -> str:
        """
        Return color to show on legend. If color is not set, color is tried to be read from layer style.

        Returns
        -------
        str
            Color string (name/rgb/hex/etc.) to be used on legend in frontend.
        """
        if self.color:
            return self.color
        return utils.get_color(self.get_layer_id())

    def get_layer_id(self):
        if self.layer_id:
            return self.layer_id
        return self.layer.id

    @property
    def model(self):
        if self.layer:
            return self.layer.model
        return layers.get_layer_by_id(self.get_layer_id()).model


LEGEND = {
    "Renewables": [
        LegendLayer("Windturbinen", "", layer_id="wind", color="blue"),
        LegendLayer("Aufdach-PV", "", layer_id="pvroof", color="yellow"),
        LegendLayer("Boden-PV", "", layer_id="pvground"),
        LegendLayer("Hydro", "", layer_id="hydro"),
        LegendLayer("Biomasse", "", layer_id="biomass"),
        LegendLayer("Fossile Kraftwerke", "", layer_id="combustion"),
    ],
}
