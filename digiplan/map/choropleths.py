"""Module to support choropleths in digiplan."""

import abc
from typing import Optional

from django.conf import settings
from django.http.response import JsonResponse

from . import calculations


class Choropleth:
    """Base class for choropleths."""

    def __init__(self, lookup: str, map_state: Optional[dict] = None) -> None:
        """
        Initialize choropleth.

        Parameters
        ----------
        lookup : str
            given lookup name
        map_state : dict
            current state of map (comes from mapengine)
        """
        self.lookup = lookup
        self.map_state = map_state

    @abc.abstractmethod
    def get_values_per_feature(self) -> dict[int, float]:
        """Must be overwritten by child class."""

    @staticmethod
    def get_paint_properties() -> dict:
        """
        Return paint properties for choropleth.

        Can be overwritten by child class.

        Returns
        -------
        dict
            containing paint properties for choropleth layer in maplibre
        """
        return {"fill-opacity": 1}

    def get_fill_color(self, values: dict[int, float]) -> dict:
        """
        Return fill colors interpolation depending on given values and lookup.

        Parameters
        ----------
        values: dict[int, float]
            values per feature ID

        Returns
        -------
        dict
            containing fill-color steps for given values
        """
        return settings.MAP_ENGINE_CHOROPLETH_STYLES.get_fill_color(self.lookup, list(values.values()))

    def render(self) -> JsonResponse:
        """
        Return values and paint properties to show choropleth layer with maplibre.

        Returns
        -------
        JsonResponse
            containing values and related paint properties to show choropleth on map
        """
        values = self.get_values_per_feature()
        paint_properties = self.get_paint_properties()
        paint_properties["fill-color"] = self.get_fill_color(values)
        return JsonResponse({"values": self.get_values_per_feature(), "paintProperties": paint_properties})


class RenewableElectricityProductionChoropleth(Choropleth):
    """Choropleth for renewable electricity production."""

    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return calculations.capacity_choropleth()


CHOROPLETHS: dict[str, type(Choropleth)] = {
    "renewable_electricity_production": RenewableElectricityProductionChoropleth,
}
