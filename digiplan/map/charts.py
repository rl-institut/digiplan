"""Module for extracting structure and data for charts."""

import json
import pathlib
from collections import namedtuple
from collections.abc import Callable
from typing import Any, Optional

from digiplan.map import calculations, config
from digiplan.map.utils import merge_dicts


CHARTS: dict[str, Callable] = {
    "capacity": calculations.capacity_chart,
    "capacity_square": calculations.capacity_square_chart,
    "population": models.Population.population_history,
    "population_density": models.Population.density_history,
    "wind_turbines": models.WindTurbine.wind_turbines_history,
    "wind_turbines_square": models.WindTurbine.wind_turbines_per_area_history,
    "detailed_overview": calculations.detailed_overview,
}

ResultChart = namedtuple("ResultChart", ("chart", "div_id"))


class Chart:
    lookup: str = None
    chart_data_function: Callable = None

    def __init__(self, lookup: Optional[str] = None, chart_data: Optional[Any] = None) -> None:
        if lookup:
            self.lookup = lookup
        self.chart_data = chart_data or self.get_chart_data()
        self.chart_options = self.get_chart_options()

    def render(self) -> dict:
        """
        Create chart based on given lookup and municipality ID or result option.

        Parameters
        ----------

        Returns
        -------
        dict
            Containing chart filled with data

        """
        if self.chart_data:
            series_type = self.chart_options["series"][0]["type"]
            series_length = len(self.chart_options["series"])
            if series_type == "line":
                data = []
                for key, value in self.chart_data:
                    year_as_string = f"{key}"
                    data.append([year_as_string, value])
                self.chart_options["series"][0]["data"] = data
            elif series_length > 1:
                for i in range(0, series_length):
                    self.chart_options["series"][i]["data"] = self.chart_data[i]
            else:
                self.chart_options["series"][0]["data"] = self.chart_data

        return self.chart_options

    def get_chart_options(self) -> dict:
        """
        Get the options for a chart from the corresponding json file.

        Returns
        -------
        dict
            Containing the json that can be filled with data

        Raises
        ------
        LookupError
            if lookup can't be found in LOOKUPS
        """
        lookup_path = pathlib.Path(config.CHARTS_DIR.path(f"{self.lookup}.json"))
        if not lookup_path.exists():
            error_msg = f"Could not find lookup '{self.lookup}' in charts folder."
            raise LookupError(error_msg)

        with lookup_path.open("r", encoding="utf-8") as lookup_json:
            lookup_options = json.load(lookup_json)

        with pathlib.Path(config.CHARTS_DIR.path("general_options.json")).open(
            "r", encoding="utf-8",
        ) as general_chart_json:
            general_chart_options = json.load(general_chart_json)

        options = merge_dicts(general_chart_options, lookup_options)
        return options

    def get_chart_data(self):
        if self.chart_data_function:
            return self.chart_data_function()
        return None


class ElectricityOverviewChart(Chart):
    lookup = "electricity_overview"
    chart_data_function = calculations.electricity_overview

    def __init__(self, simulation_id) -> None:
        self.simulation_id = simulation_id
        super().__init__()

    def get_chart_data(self):  # noqa: D102, ANN201
        return self.chart_data_function(self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for item in self.chart_options["series"]:
            try:
                profile = config.SIMULATION_RENEWABLES[item["name"]]
                item["data"][2] = self.chart_data[profile]
            except KeyError:
                profile = config.SIMULATION_DEMANDS[item["name"]]
                item["data"][0] = self.chart_data[profile]

        return self.chart_options


RESULT_CHARTS = (ResultChart(ElectricityOverviewChart, "electricity_overview_chart"),)

CHARTS: dict[str, Callable] = {}


def create_chart(lookup: str, chart_data: Optional[Any] = None) -> dict:
    if lookup in CHARTS:
        return CHARTS[lookup](lookup, chart_data).render()
    else:
        return Chart(lookup, chart_data).render()
