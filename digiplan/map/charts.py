"""Module for extracting structure and data for charts."""

import json
import pathlib
from typing import Any, Optional

from django.utils.translation import gettext_lazy as _

from digiplan.map import calculations, config, models
from digiplan.map.utils import merge_dicts


class Chart:
    """Base class for charts."""

    lookup: str = None

    def __init__(
        self,
        lookup: Optional[str] = None,
        chart_data: Optional[Any] = None,
        **kwargs,  # noqa: ARG002
    ) -> None:
        """Initialize chart data and chart options."""
        if lookup:
            self.lookup = lookup
        self.chart_data = chart_data if chart_data is not None else self.get_chart_data()
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
                for key, value in self.chart_data.items():
                    year_as_string = f"{key}"
                    data.append([year_as_string, value])
                self.chart_options["series"][0]["data"] = data
            elif series_length > 1:
                for i in range(0, series_length):
                    values = self.chart_data[i]
                    if not isinstance(values, (list, tuple)):
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


class SimulationChart(Chart):
    """For charts based on simulations."""

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


class PopulationRegionChart(Chart):
    """Chart for regional population."""

    lookup = "population"

    def get_chart_data(self) -> None:
        """Calculate population for whole region."""
        return models.Population.quantity_per_municipality_per_year().sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        return chart_options


class PopulationDensityRegionChart(Chart):
    """Chart for regional population density."""

    lookup = "population"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.calculate_square_for_value(models.Population.quantity_per_municipality_per_year()).sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("EW/km²")
        return chart_options


class EmployeesRegionChart(Chart):
    """Chart for regional employees."""

    lookup = "wind_turbines"

    def get_chart_data(self) -> list:
        """Calculate population for whole region."""
        return [int(calculations.employment_per_municipality().sum())]

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("")
        del chart_options["series"][0]["name"]
        return chart_options


class CompaniesRegionChart(Chart):
    """Chart for regional companies."""

    lookup = "wind_turbines"

    def get_chart_data(self) -> list:
        """Calculate population for whole region."""
        return [int(calculations.companies_per_municipality().sum())]

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("")
        del chart_options["series"][0]["name"]
        return chart_options


class CapacityRegionChart(Chart):
    """Chart for regional capacities."""

    lookup = "capacity"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.capacities_per_municipality().sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        return chart_options


class CapacitySquareRegionChart(Chart):
    """Chart for regional capacities per square meter."""

    lookup = "capacity"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.calculate_square_for_value(calculations.capacities_per_municipality()).sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("MW")
        return chart_options


class EnergyRegionChart(Chart):
    """Chart for regional energy."""

    lookup = "capacity"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.energies_per_municipality().sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("GWh")
        return chart_options


class Energy2045RegionChart(SimulationChart):
    """Chart for regional energy."""

    lookup = "capacity"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        status_quo_data = calculations.energies_per_municipality().sum()
        future_data = calculations.energies_per_municipality_2045(self.simulation_id).sum()
        return list(zip(status_quo_data, future_data))

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("MWh")
        chart_options["xAxis"]["data"] = ["Status Quo", "Mein Szenario"]
        return chart_options


class EnergyShareRegionChart(Chart):
    """Chart for regional energy shares."""

    lookup = "capacity"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.energy_shares_per_municipality().sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("%")
        return chart_options


class EnergyCapitaRegionChart(Chart):
    """Chart for regional energy shares per capita."""

    lookup = "capacity"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.calculate_capita_for_value(calculations.energy_shares_per_municipality()).sum() * 1e3

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("MWh")
        return chart_options


class EnergySquareRegionChart(Chart):
    """Chart for regional energy shares per square meter."""

    lookup = "capacity"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.calculate_square_for_value(calculations.energy_shares_per_municipality()).sum() * 1e3

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("MWh")
        return chart_options


class WindTurbinesRegionChart(Chart):
    """Chart for regional wind turbines."""

    lookup = "wind_turbines"

    def get_chart_data(self) -> list[int]:
        """Calculate population for whole region."""
        return [int(models.WindTurbine.quantity_per_municipality().sum())]

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        return chart_options


class WindTurbinesSquareRegionChart(Chart):
    """Chart for regional wind turbines per square meter."""

    lookup = "wind_turbines"

    def get_chart_data(self) -> list[float]:
        """Calculate population for whole region."""
        return [float(calculations.calculate_square_for_value(models.WindTurbine.quantity_per_municipality()).sum())]

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("")
        return chart_options


class ElectricityDemandRegionChart(Chart):
    """Chart for regional electricity demand."""

    lookup = "electricity_demand"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.electricity_demand_per_municipality().sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("GWh")
        return chart_options


class ElectricityDemandCapitaRegionChart(Chart):
    """Chart for regional electricity demand per population."""

    lookup = "electricity_demand"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.calculate_capita_for_value(calculations.electricity_demand_per_municipality()).sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("kWh")
        return chart_options


class HeatDemandRegionChart(Chart):
    """Chart for regional heat demand."""

    lookup = "heat_demand"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.heat_demand_per_municipality().sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("GWh")
        return chart_options


class HeatDemandCapitaRegionChart(Chart):
    """Chart for regional heat demand per population."""

    lookup = "heat_demand"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.calculate_capita_for_value(calculations.heat_demand_per_municipality()).sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("kWh")
        return chart_options


class BatteriesRegionChart(Chart):
    """Chart for regional battery count."""

    lookup = "wind_turbines"

    def get_chart_data(self) -> list:
        """Calculate population for whole region."""
        return [int(calculations.batteries_per_municipality().sum())]

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("#")
        del chart_options["series"][0]["name"]
        return chart_options


class BatteriesCapacityRegionChart(Chart):
    """Chart for regional battery capacity."""

    lookup = "wind_turbines"

    def get_chart_data(self) -> list:
        """Calculate population for whole region."""
        return [int(calculations.battery_capacities_per_municipality().sum())]

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("#")
        del chart_options["series"][0]["name"]
        return chart_options


CHARTS: dict[str, type[Chart]] = {
    "electricity_overview": ElectricityOverviewChart,
    "heat_overview": HeatOverviewChart,
    "population_statusquo_region": PopulationRegionChart,
    "population_density_statusquo_region": PopulationDensityRegionChart,
    "employees_statusquo_region": EmployeesRegionChart,
    "companies_statusquo_region": CompaniesRegionChart,
    "capacity_statusquo_region": CapacityRegionChart,
    "capacity_square_statusquo_region": CapacitySquareRegionChart,
    "energy_statusquo_region": EnergyRegionChart,
    "energy_2045_region": Energy2045RegionChart,
    "energy_share_statusquo_region": EnergyShareRegionChart,
    "energy_capita_statusquo_region": EnergyCapitaRegionChart,
    "energy_square_statusquo_region": EnergySquareRegionChart,
    "wind_turbines_statusquo_region": WindTurbinesRegionChart,
    "wind_turbines_square_statusquo_region": WindTurbinesSquareRegionChart,
    "electricity_demand_statusquo_region": ElectricityDemandRegionChart,
    "electricity_demand_capita_statusquo_region": ElectricityDemandCapitaRegionChart,
    "heat_demand_statusquo_region": HeatDemandRegionChart,
    "heat_demand_capita_statusquo_region": HeatDemandCapitaRegionChart,
    "batteries_statusquo_region": BatteriesRegionChart,
    "batteries_capacity_statusquo_region": BatteriesCapacityRegionChart,
}


def create_chart(lookup: str, chart_data: Optional[Any] = None) -> dict:
    """
    Return chart for given lookup.

    If chart is listed in CHARTS, specific chart is returned. Otherwise, generic chart is returned.
    """
    if lookup in CHARTS:
        return CHARTS[lookup](lookup, chart_data).render()
    return Chart(lookup, chart_data).render()
