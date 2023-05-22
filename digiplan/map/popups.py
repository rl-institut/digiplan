import abc
import json
import pathlib
from typing import Iterable, Optional

from django_mapengine import popups
from django_oemof import results
from oemoflex.postprocessing import core, postprocessing

from . import calculations, charts, config, models


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
        chart_data = self.get_chart_data()
        chart = charts.create_chart(self.lookup, chart_data)
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


class SimulationPopup(RegionPopup, abc.ABC):
    calculation = None

    def __init__(self, lookup: str, selected_id: int, map_state: Optional[dict] = None, template: Optional[str] = None):
        super().__init__(lookup, selected_id, map_state, template)
        self.simulation_id = map_state["simulation_id"]
        self.result = list(results.get_results(self.simulation_id, [self.calculation]).values())[0]


class CapacityPopup(RegionPopup):
    def get_region_value(self) -> float:
        return calculations.capacity_popup()

    def get_municipality_value(self) -> float:
        return calculations.capacity_popup(self.selected_id)

    def get_chart_data(self) -> Iterable:
        return calculations.capacity_chart(self.selected_id)


class RenewableElectricityProductionPopup(SimulationPopup):
    calculation = core.ParametrizedCalculation(
        postprocessing.AggregatedFlows,
        {
            "from_nodes": [
                "ABW-solar-pv_ground",
            ]
        },
    )

    def get_region_value(self) -> float:
        return self.result

    def get_municipality_value(self) -> float:
        return calculations.capacity_popup(self.selected_id)

    def get_chart_data(self) -> Iterable:
        return calculations.capacity_chart(self.selected_id)


POPUPS: dict[str, type(popups.Popup)] = {
    "capacity": CapacityPopup,
    "renewable_electricity_production": RenewableElectricityProductionPopup,
}
