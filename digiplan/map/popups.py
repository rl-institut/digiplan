import abc
import json
import pathlib
from typing import Iterable

import jsonschema
from django_mapengine import popups

from config import schemas

from . import config, models
from .results import calculations


class RegionPopup(popups.ChartPopup):
    def get_context_data(self) -> dict:
        with pathlib.Path(config.POPUPS_DIR.path(f"{self.lookup}.json")).open("r", encoding="utf-8") as data_json:
            data = json.load(data_json)

        data["id"] = self.selected_id
        data["data"]["region_value"] = self.get_region_value()
        data["data"]["municipality_value"] = self.get_municipality_value()
        data["municipality"] = models.Municipality.objects.get(pk=self.selected_id)

        return data

    def get_chart_options(self) -> dict:
        with pathlib.Path(config.POPUPS_DIR.path(f"{self.lookup}_chart.json")).open(
            "r", encoding="utf-8"
        ) as chart_json:
            chart = json.load(chart_json)
        chart_data = self.get_chart_data()
        chart["series"][0]["data"] = [{"key": key, "value": value} for key, value in chart_data]
        jsonschema.validate(chart, schemas.CHART_SCHEMA)
        return chart

    @abc.abstractmethod
    def get_region_value(self) -> float:
        """Must be overwritten"""

    @abc.abstractmethod
    def get_municipality_value(self) -> float:
        """Must be overwritten"""

    @abc.abstractmethod
    def get_chart_data(self) -> Iterable:
        """Must be overwritten"""


class CapacityPopup(RegionPopup):
    def get_region_value(self) -> float:
        return calculations.capacity_popup()

    def get_municipality_value(self) -> float:
        return calculations.capacity_popup(self.selected_id)

    def get_chart_data(self) -> Iterable:
        return calculations.capacity_chart(self.selected_id)


POPUPS: dict[str, type(popups.Popup)] = {"capacity": CapacityPopup}
