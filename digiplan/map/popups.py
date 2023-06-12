"""Provide popups for digiplan."""

import abc
import json
import pathlib
from collections.abc import Iterable
from typing import Optional, Union

from django_mapengine import popups
from django_oemof import results
from oemof.tabular.postprocessing import core

from . import calculations, charts, config, models


class RegionPopup(popups.ChartPopup):
    """Popup containing values for municipality and region in header."""

    unit: str = None

    def get_context_data(self) -> dict:
        """
        Set up context data including municipality and region values.

        Returns
        -------
        dict
            context dict including region and municipality data
        """
        with pathlib.Path(config.POPUPS_DIR.path(f"{self.lookup}.json")).open("r", encoding="utf-8") as data_json:
            data = json.load(data_json)

        data["id"] = self.selected_id
        data["data"]["region_value"] = self.get_region_value()
        data["data"]["municipality_value"] = self.get_municipality_value()
        data["data"]["unit"] = self.unit
        data["municipality"] = models.Municipality.objects.get(pk=self.selected_id)

        return data

    def get_chart_options(self) -> dict:
        """
        Return chart data to build chart from in JS.

        Returns
        -------
        dict
            chart data ready to use in ECharts in JS
        """
        chart_data = self.get_chart_data()
        return charts.create_chart(self.lookup, chart_data)

    @abc.abstractmethod
    def get_region_value(self) -> float:
        """Must be overwritten."""

    @abc.abstractmethod
    def get_municipality_value(self) -> Optional[float]:
        """Must be overwritten."""

    @abc.abstractmethod
    def get_chart_data(self) -> Iterable:
        """Must be overwritten."""


class SimulationPopup(RegionPopup, abc.ABC):
    """Popup with simulation based context."""

    calculation: Union[core.Calculation, core.ParametrizedCalculation] = None

    def __init__(
        self,
        lookup: str,
        selected_id: int,
        map_state: Optional[dict] = None,
        template: Optional[str] = None,
    ) -> None:
        """
        Init simulation popup.

        Parameters
        ----------
        lookup: str
            Lookup name
        selected_id: int
            ID of selected feature
        map_state: Optional[dict]
            Current state of map. Includes current simulation ID
        template: Optional[str]
            Template to render popup. If not given template using lookup name is used
        """
        super().__init__(lookup, selected_id, map_state, template)
        self.simulation_id = map_state["simulation_id"]
        self.result = list(results.get_results(self.simulation_id, [self.calculation]).values())[0]


class CapacityPopup(RegionPopup):
    """Popup to show capacities."""

    def get_region_value(self) -> float:  # noqa: D102
        return calculations.capacity_popup()

    def get_municipality_value(self) -> float:  # noqa: D102
        return calculations.capacity_popup(self.selected_id)

    def get_chart_data(self) -> Iterable:  # noqa: D102
        return calculations.capacity_chart(self.selected_id)


class CapacitySquarePopup(RegionPopup):
    def get_region_value(self) -> float:
        return calculations.capacity_square_popup

    def get_municipality_value(self) -> float:
        return calculations.capacity_square_popup(self.selected_id)

    def get_chart_data(self) -> Iterable:
        return calculations.capacity_square_chart(self.selected_id)


class PopulationPopup(RegionPopup):
    def get_region_value(self) -> float:
        return models.Population.quantity

    def get_municipality_value(self) -> float:
        return models.Population.quantity(self.selected_id)

    def get_chart_data(self) -> Iterable:
        return models.Population.population_history(self.selected_id)


class RenewableElectricityProductionPopup(SimulationPopup):
    """Popup to show renewable electricity production values."""

    unit = "MWh"
    calculation = calculations.electricity_production

    def get_region_value(self) -> float:  # noqa: D102
        return self.result.sum() / 1000

    def get_municipality_value(self) -> Optional[float]:  # noqa: D102
        return None

    def get_chart_data(self) -> Iterable:  # noqa: D102
        self.result.index = self.result.index.map(lambda x: config.SIMULATION_NAME_MAPPING[x[0]])
        return self.result


POPUPS: dict[str, type(popups.Popup)] = {
    "capacity": CapacityPopup,
    "capacity_square": CapacitySquarePopup,
    "population": PopulationPopup,
    "renewable_electricity_production": RenewableElectricityProductionPopup,
}
