"""Module for extracting structure and data for charts."""

import json
import pathlib
from collections import namedtuple
from collections.abc import Callable
from typing import Any, Optional

from digiplan.map import calculations, config, models
from digiplan.map.utils import merge_dicts

CHARTS: dict[str, Callable] = {
    "capacity": calculations.capacity_comparison,
    "capacity_square": calculations.capacity_square_comparison,
    "population": models.Population.population_history,
    "population_density": models.Population.density_history,
    "wind_turbines": models.WindTurbine.wind_turbines_history,
    "wind_turbines_square": models.WindTurbine.wind_turbines_per_area_history,
    "detailed_overview": calculations.detailed_overview,
}

ResultChart = namedtuple("ResultChart", ("chart", "div_id"))


class Chart:
    """Base class for charts."""

    lookup: str = None

    def __init__(self, lookup: Optional[str] = None, chart_data: Optional[Any] = None) -> None:
        """Initialize chart data and chart options."""
        if lookup:
            self.lookup = lookup
        self.chart_data = chart_data or self.get_chart_data()
        self.chart_options = self.get_chart_options()

    def render(self) -> dict:
        """
        Create chart based on given lookup and municipality ID or result option.

        Returns
        -------
        dict
            Containing chart filled with data

        """
        if self.chart_data is not None:
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
                    values = self.chart_data[i]
                    if not isinstance(values, list):
                        values = [values]
                    self.chart_options["series"][i]["data"] = values
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
            "r",
            encoding="utf-8",
        ) as general_chart_json:
            general_chart_options = json.load(general_chart_json)

        options = merge_dicts(general_chart_options, lookup_options)
        return options

    def get_chart_data(self) -> None:
        """
        Check if chart_data_function is valid.

        Returns
        -------
        None

        """
        return


class DetailedOverviewChart(Chart):
    """Detailed Overview Chart."""

    lookup = "detailed_overview"

    def __init__(self, simulation_id: int) -> None:
        """
        Init Detailed Overview Chart.

        Parameters
        ----------
        simulation_id: any
            id of used Simulation
        """
        self.simulation_id = simulation_id
        super().__init__()

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.detailed_overview(simulation_id=self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for item in self.chart_options["series"]:
            profile = config.SIMULATION_NAME_MAPPING[item["name"]]
            item["data"][1] = self.chart_data[profile]

        return self.chart_options


class CTSOverviewChart(Chart):
    """CTS Overview Chart. Shows greenhouse gas emissions."""

    lookup = "ghg_overview"

    def __init__(self, simulation_id: int) -> None:
        """
        Init CTS Overview Chart.

        Parameters
        ----------
        simulation_id: any
            id of used Simulation
        """
        self.simulation_id = simulation_id
        super().__init__()

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.detailed_overview(simulation_id=self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for item in self.chart_options["series"]:
            profile = config.SIMULATION_NAME_MAPPING[item["name"]]
            item["data"][2] = self.chart_data[profile]

        return self.chart_options


class ElectricityOverviewChart(Chart):
    """Chart for electricity overview."""

    lookup = "electricity_overview"

    def __init__(self, simulation_id: int) -> None:
        """Store simulation ID."""
        self.simulation_id = simulation_id
        super().__init__()

    def get_chart_data(self):  # noqa: ANN201
        """Get chart data from electricity overview calculation."""
        return calculations.electricity_overview(simulation_id=self.simulation_id)

    def render(self) -> dict:
        """Overwrite render function."""
        self.chart_options["series"][0]["data"][2] = self.chart_data["ABW-wind-onshore"]
        self.chart_options["series"][1]["data"][2] = self.chart_data["ABW-solar-pv_ground"]
        self.chart_options["series"][2]["data"][2] = self.chart_data["ABW-solar-pv_rooftop"]
        self.chart_options["series"][3]["data"][2] = self.chart_data["ABW-biomass"]
        self.chart_options["series"][4]["data"][2] = self.chart_data["ABW-hydro-ror"]
        self.chart_options["series"][5]["data"][0] = self.chart_data["ABW-electricity-demand_cts"]
        self.chart_options["series"][6]["data"][0] = self.chart_data["electricity_heat_demand_cts"]
        self.chart_options["series"][7]["data"][0] = self.chart_data["ABW-electricity-demand_hh"]
        self.chart_options["series"][8]["data"][0] = self.chart_data["electricity_heat_demand_hh"]
        self.chart_options["series"][9]["data"][0] = self.chart_data["ABW-electricity-demand_ind"]
        self.chart_options["series"][10]["data"][0] = self.chart_data["electricity_heat_demand_ind"]
        self.chart_options["series"][11]["data"][0] = self.chart_data["ABW-electricity-bev_charging"]
        return self.chart_options


class ElectricityCTSChart(Chart):
    """Electricity CTS Chart. Shows greenhouse gas emissions."""

    lookup = "electricity_ghg"

    def __init__(self, simulation_id: int) -> None:
        """
        Init Electricity CTS Chart.

        Parameters
        ----------
        simulation_id: any
            id of used Simulation
        """
        self.simulation_id = simulation_id
        super().__init__()

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.detailed_overview(simulation_id=self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for item in self.chart_options["series"]:
            profile = config.SIMULATION_NAME_MAPPING[item["name"]]
            item["data"][2] = self.chart_data[profile]

        return self.chart_options


class HeatOverviewChart(Chart):
    """Heat Overview Chart."""

    lookup = "overview_heat"

    def __init__(self, simulation_id: int) -> None:
        """
        Init Heat Overview Chart.

        Parameters
        ----------
        simulation_id: any
            id of used Simulation
        """
        self.simulation_id = simulation_id
        super().__init__()

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.heat_overview(simulation_id=self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for item in self.chart_options["series"]:
            profile = config.SIMULATION_NAME_MAPPING[item["name"]]
            item["data"][1] = self.chart_data[profile]

        return self.chart_options


class HeatProductionChart(Chart):
    """Heat Production Chart. Shows decentralized and centralized heat."""

    lookup = "decentralized_centralized_heat"

    def __init__(self, simulation_id: int) -> None:
        """
        Init Heat Production Chart.

        Parameters
        ----------
        simulation_id: any
            id of used Simulation
        """
        self.simulation_id = simulation_id
        super().__init__()

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.heat_overview(simulation_id=self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for item in self.chart_options["series"]:
            profile = config.SIMULATION_NAME_MAPPING[item["name"]]
            item["data"][1] = self.chart_data[profile]

        return self.chart_options


class MobilityOverviewChart(Chart):
    """Mobility Overview Chart. Shows Number of Cars."""

    lookup = "mobility_overview"

    def __init__(self, simulation_id: int) -> None:
        """
        Init Mobility Overview Chart.

        Parameters
        ----------
        simulation_id: any
            id of used Simulation
        """
        self.simulation_id = simulation_id
        super().__init__()

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.heat_overview(simulation_id=self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for item in self.chart_options["series"]:
            profile = config.SIMULATION_NAME_MAPPING[item["name"]]
            item["data"][1] = self.chart_data[profile]

        return self.chart_options


class MobilityCTSChart(Chart):
    """Mobility CTS Chart. Shows greenhouse gas emissions."""

    lookup = "mobility_ghg"

    def __init__(self, simulation_id: int) -> None:
        """
        Init Mobility CTS Chart.

        Parameters
        ----------
        simulation_id: any
            id of used Simulation
        """
        self.simulation_id = simulation_id
        super().__init__()

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.detailed_overview(simulation_id=self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for item in self.chart_options["series"]:
            profile = config.SIMULATION_NAME_MAPPING[item["name"]]
            item["data"][2] = self.chart_data[profile]

        return self.chart_options


RESULT_CHARTS = (
    ResultChart(ElectricityOverviewChart, "electricity_overview_chart"),
    ResultChart(HeatOverviewChart, "overview_heat_chart"),
)


def create_chart(lookup: str, chart_data: Optional[Any] = None) -> dict:
    """
    Return chart for given lookup.

    If chart is listed in CHARTS, specific chart is returned. Otherwise, generic chart is returned.
    """
    if lookup in CHARTS:
        return CHARTS[lookup](lookup, chart_data).render()
    return Chart(lookup, chart_data).render()
