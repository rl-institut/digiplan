"""Module for extracting structure and data for charts."""

import json
import pathlib
from typing import Any, Optional

import pandas as pd
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


class DetailedOverviewChart(SimulationChart):
    """Detailed Overview Chart."""

    lookup = "detailed_overview"

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.electricity_overview(simulation_id=self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for i, item in enumerate(self.chart_options["series"]):
            item["data"][1] = self.chart_data.iloc[i]
        return self.chart_options


class GHGReductionChart(SimulationChart):
    """GHG Reduction Chart. Shows greenhouse gas emissions."""

    lookup = "ghg_reduction"

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.get_reduction(simulation_id=self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        # Enter import and energy from renewables
        for i, item in enumerate(self.chart_options["series"][7:9]):
            item["data"][1] = self.chart_data[i]
        # Calculate emission offset
        summed_emissions_2019 = sum(item["data"][0] for item in self.chart_options["series"][:7])
        self.chart_options["series"][0]["data"][1] = summed_emissions_2019 - sum(self.chart_data)
        return self.chart_options


class ElectricityOverviewChart(SimulationChart):
    """Chart for electricity overview."""

    lookup = "electricity_overview"

    def get_chart_data(self):  # noqa: ANN201
        """Get chart data from electricity overview calculation."""
        return {
            "2022": calculations.electricity_overview(2022),
            "2045": calculations.electricity_overview(2045),
            "user": calculations.electricity_overview_from_user(simulation_id=self.simulation_id),
        }

    def render(self) -> dict:  # noqa: D102
        mapping = {
            "Aufdach-PV": ("ABW-solar-pv_rooftop", "pv_roof"),
            "Bioenergie": ("ABW-biomass", ""),
            "Export*": ("ABW-electricity-export", ""),
            "Freiflächen-PV": ("ABW-solar-pv_grund", "pv_ground"),
            "Import*": ("ABW-electricity-import", ""),
            "Verbrauch GHD": ("ABW-electricity-demand_cts", "Strombedarf GDP"),
            "Verbrauch Haushalte": ("ABW-electricity-demand_hh", "Strombedarf Haushalte"),
            "Verbrauch Industrie": ("ABW-electricity-demand_ind", "Strombedarf Industrie"),
            "Wasserkraft": ("ABW-hydro-ror", "ror"),
            "Windenergie": ("ABW-wind-onshore", "wind"),
        }
        for _i, item in enumerate(self.chart_options["series"]):
            mapped_keys = mapping[item["name"]]
            item["data"][0] = round(
                self.chart_data["2022"].get(mapped_keys[0], self.chart_data["2022"].get(mapped_keys[1], 0.0)),
            )
            item["data"][1] = round(
                self.chart_data["user"].get(mapped_keys[0], self.chart_data["user"].get(mapped_keys[1], 0.0)),
            )
            item["data"][2] = round(
                self.chart_data["2045"].get(mapped_keys[0], self.chart_data["2045"].get(mapped_keys[1], 0.0)),
            )
        return self.chart_options


class ElectricityAutarkyChart(SimulationChart):
    """Chart for electricity autarky."""

    lookup = "electricity_autarky"

    def get_chart_data(self):  # noqa: ANN201
        """Get chart data from electricity overview calculation."""
        return calculations.get_regional_independency(self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for i, item in enumerate(self.chart_options["series"]):
            item["data"][0] = self.chart_data[i + 2]
            item["data"][1] = self.chart_data[i]
        return self.chart_options


class ElectricityCTSChart(SimulationChart):
    """Electricity CTS Chart. Shows greenhouse gas emissions."""

    lookup = "electricity_autarky"

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.detailed_overview(simulation_id=self.simulation_id)

    def render(self) -> dict:  # noqa: D102
        for item in self.chart_options["series"]:
            profile = config.SIMULATION_NAME_MAPPING[item["name"]]
            item["data"][2] = self.chart_data[profile]

        return self.chart_options


class HeatStructureChart(SimulationChart):
    """Heat Structure Chart."""

    def render(self) -> dict:  # noqa: D102
        mapping = {
            "Erdgas": ("methane", "ch4_bpchp", "ch4_extchp"),
            "Heizöl": ("fuel_oil",),
            "Holz": ("wood_oven", "wood_bpchp", "wood_extchp"),
            "Wärmepumpe": ("heat_pump",),
            "El. Direktheizung": ("electricity_direct_heating",),
            "Biogas": ("biogas_bpchp",),
            "Solarthermie": ("solar_thermal",),
            "Sonstige": ("other",),
            "Verbrauch Haushalte": ("heat-demand-hh",),
            "Verbrauch GHD": ("heat-demand-cts",),
            "Verbrauch Industrie": ("heat-demand-ind",),
        }
        for _i, item in enumerate(self.chart_options["series"]):
            item["data"][0] = round(
                sum(self.chart_data["2045"].get(entry, 0.0) for entry in mapping[item["name"]]) * 1e-3,
            )
            item["data"][1] = round(
                sum(self.chart_data["user"].get(entry, 0.0) for entry in mapping[item["name"]]) * 1e-3,
            )
            item["data"][2] = round(
                sum(self.chart_data["2022"].get(entry, 0.0) for entry in mapping[item["name"]]) * 1e-3,
            )
        return self.chart_options


class HeatStructureCentralChart(HeatStructureChart):
    """Heat structure for centralized heat."""

    lookup = "heat_centralized"

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.heat_overview(simulation_id=self.simulation_id, distribution="central")


class HeatStructureDecentralChart(HeatStructureChart):
    """Heat structure for decentralized heat."""

    lookup = "heat_decentralized"

    def get_chart_data(self):  # noqa: D102, ANN201
        return calculations.heat_overview(simulation_id=self.simulation_id, distribution="decentral")


class GhgHistoryChart(SimulationChart):
    """GHG history chart."""

    lookup = "ghg_history"

    def get_chart_data(self):  # noqa: D102, ANN201
        # TODO(Hendrik): Get static data from digipipe datapackage  # noqa: TD003
        return pd.DataFrame()

    def render(self) -> dict:  # noqa: D102
        for item in self.chart_options["series"]:
            profile = config.SIMULATION_NAME_MAPPING[item["name"]]
            item["data"][1] = self.chart_data[profile]

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
        return calculations.calculate_square_for_value(
            pd.DataFrame(models.Population.quantity_per_municipality_per_year().sum()).transpose(),
        ).sum()

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
        chart_options["yAxis"]["name"] = "#"
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
        chart_options["yAxis"]["name"] = "#"
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


class Capacity2045RegionChart(SimulationChart):
    """Chart for regional capacities in 2045."""

    lookup = "capacity"

    def get_chart_data(self) -> list:
        """Calculate capacities for whole region."""
        status_quo_data = calculations.capacities_per_municipality().sum()
        future_data = calculations.capacities_per_municipality_2045(self.simulation_id).sum()
        return list(zip(status_quo_data, future_data))

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        chart_options["xAxis"]["data"] = ["Status Quo", "Mein Szenario"]
        del chart_options["title"]["text"]
        return chart_options


class CapacitySquareRegionChart(Chart):
    """Chart for regional capacities per square meter."""

    lookup = "capacity"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return calculations.calculate_square_for_value(
            pd.DataFrame(calculations.capacities_per_municipality().sum()).transpose(),
        ).sum()

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("MW")
        return chart_options


class CapacitySquare2045RegionChart(SimulationChart):
    """Chart for regional capacities in 2045."""

    lookup = "capacity"

    def get_chart_data(self) -> list:
        """Calculate capacities for whole region."""
        status_quo_data = calculations.calculate_square_for_value(
            pd.DataFrame(calculations.capacities_per_municipality().sum()).transpose(),
        ).sum()
        future_data = calculations.calculate_square_for_value(
            pd.DataFrame(calculations.capacities_per_municipality_2045(self.simulation_id).sum()).transpose(),
        ).sum()
        return list(zip(status_quo_data, future_data))

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        chart_options["xAxis"]["data"] = ["Status Quo", "Mein Szenario"]
        chart_options["yAxis"]["name"] = _("MW")
        del chart_options["title"]["text"]
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
        return (
            calculations.calculate_capita_for_value(
                pd.DataFrame(calculations.energies_per_municipality().sum()).transpose(),
            ).sum()
            * 1e3
        )

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
        return (
            calculations.calculate_square_for_value(
                pd.DataFrame(calculations.energies_per_municipality().sum()).transpose(),
            ).sum()
            * 1e3
        )

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


class WindTurbines2045RegionChart(SimulationChart):
    """Chart for regional wind turbines in 2045."""

    lookup = "wind_turbines"

    def get_chart_data(self) -> list[int]:
        """Calculate population for whole region."""
        status_quo_data = models.WindTurbine.quantity_per_municipality().sum()
        future_data = calculations.wind_turbines_per_municipality_2045(self.simulation_id).sum()
        return [int(status_quo_data), int(future_data)]

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        chart_options["xAxis"]["data"] = ["Status Quo", "Mein Szenario"]
        del chart_options["title"]["text"]
        return chart_options


class WindTurbinesSquareRegionChart(Chart):
    """Chart for regional wind turbines per square meter."""

    lookup = "wind_turbines"

    def get_chart_data(self) -> list[float]:
        """Calculate population for whole region."""
        return [
            float(
                calculations.calculate_square_for_value(
                    pd.DataFrame({"turbines": models.WindTurbine.quantity_per_municipality().sum()}, index=[1]),
                ).sum(),
            ),
        ]

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = "Anzahl Windenergieanlagen"
        return chart_options


class WindTurbinesSquare2045RegionChart(SimulationChart):
    """Chart for regional wind turbines per square meter in 2045."""

    lookup = "wind_turbines"

    def get_chart_data(self) -> list[float]:
        """Calculate population for whole region."""
        status_quo_data = calculations.calculate_square_for_value(
            pd.DataFrame({"turbines": models.WindTurbine.quantity_per_municipality().sum()}, index=[1]),
        ).sum()
        future_data = calculations.calculate_square_for_value(
            pd.DataFrame(
                {"turbines": calculations.wind_turbines_per_municipality_2045(self.simulation_id).sum()},
                index=[1],
            ),
        ).sum()
        return [float(status_quo_data), float(future_data)]

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = "#"
        chart_options["xAxis"]["data"] = ["Status Quo", "Mein Szenario"]
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


class ElectricityDemand2045RegionChart(SimulationChart):
    """Chart for regional electricity demand."""

    lookup = "electricity_demand"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        status_quo_data = calculations.electricity_demand_per_municipality().sum()
        future_data = calculations.electricity_demand_per_municipality_2045(self.simulation_id).sum()
        return list(zip(status_quo_data, future_data))

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("GWh")
        chart_options["xAxis"]["data"] = ["Status Quo", "Mein Szenario"]
        return chart_options


class ElectricityDemandCapitaRegionChart(Chart):
    """Chart for regional electricity demand per population."""

    lookup = "electricity_demand"

    def get_chart_data(self) -> pd.DataFrame:
        """Calculate capacities for whole region."""
        return (
            calculations.calculate_capita_for_value(
                pd.DataFrame(calculations.electricity_demand_per_municipality().sum()).transpose(),
            ).sum()
            * 1e6
        )

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("kWh")
        return chart_options


class ElectricityDemandCapita2045RegionChart(SimulationChart):
    """Chart for regional electricity demand per population in 2045."""

    lookup = "electricity_demand"

    def get_chart_data(self) -> pd.DataFrame:
        """Calculate capacities for whole region."""
        status_quo_data = (
            calculations.calculate_capita_for_value(
                pd.DataFrame(calculations.electricity_demand_per_municipality().sum()).transpose(),
            ).sum()
            * 1e6
        )
        future_data = (
            calculations.calculate_capita_for_value(
                pd.DataFrame(
                    calculations.electricity_demand_per_municipality_2045(self.simulation_id).sum(),
                ).transpose(),
            ).sum()
            * 1e6
        )
        return list(zip(status_quo_data, future_data))

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("kWh")
        chart_options["xAxis"]["data"] = ["Status Quo", "Mein Szenario"]
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


class HeatDemand2045RegionChart(SimulationChart):
    """Chart for regional heat demand in 2045."""

    lookup = "heat_demand"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        status_quo_data = calculations.heat_demand_per_municipality().sum()
        future_data = calculations.heat_demand_per_municipality_2045(self.simulation_id).sum()
        return list(zip(status_quo_data, future_data))

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("GWh")
        chart_options["xAxis"]["data"] = ["Status Quo", "Mein Szenario"]
        return chart_options


class HeatDemandCapitaRegionChart(Chart):
    """Chart for regional heat demand per population."""

    lookup = "heat_demand"

    def get_chart_data(self) -> None:
        """Calculate capacities for whole region."""
        return (
            calculations.calculate_capita_for_value(
                pd.DataFrame(calculations.heat_demand_per_municipality().sum()).transpose(),
            ).sum()
            * 1e6
        )

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("kWh")
        return chart_options


class HeatDemandCapita2045RegionChart(SimulationChart):
    """Chart for regional heat demand per population in 2045."""

    lookup = "heat_demand"

    def get_chart_data(self) -> pd.DataFrame:
        """Calculate capacities for whole region."""
        status_quo_data = (
            calculations.calculate_capita_for_value(
                pd.DataFrame(calculations.heat_demand_per_municipality().sum()).transpose(),
            ).sum()
            * 1e6
        )
        future_data = (
            calculations.calculate_capita_for_value(
                pd.DataFrame(
                    calculations.heat_demand_per_municipality_2045(self.simulation_id).sum(),
                ).transpose(),
            ).sum()
            * 1e6
        )
        return list(zip(status_quo_data, future_data))

    def get_chart_options(self) -> dict:
        """Overwrite title and unit."""
        chart_options = super().get_chart_options()
        del chart_options["title"]["text"]
        chart_options["yAxis"]["name"] = _("kWh")
        chart_options["xAxis"]["data"] = ["Status Quo", "Mein Szenario"]
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
        chart_options["yAxis"]["name"] = _("Anzahl")
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
        chart_options["yAxis"]["name"] = _("MWh")
        del chart_options["series"][0]["name"]
        return chart_options


CHARTS: dict[str, type[Chart]] = {
    "detailed_overview": DetailedOverviewChart,
    "ghg_reduction": GHGReductionChart,
    "electricity_overview": ElectricityOverviewChart,
    "electricity_autarky": ElectricityAutarkyChart,
    "heat_decentralized": HeatStructureDecentralChart,
    "heat_centralized": HeatStructureCentralChart,
    "population_statusquo_region": PopulationRegionChart,
    "population_density_statusquo_region": PopulationDensityRegionChart,
    "employees_statusquo_region": EmployeesRegionChart,
    "companies_statusquo_region": CompaniesRegionChart,
    "capacity_statusquo_region": CapacityRegionChart,
    "capacity_square_statusquo_region": CapacitySquareRegionChart,
    "capacity_2045_region": Capacity2045RegionChart,
    "capacity_square_2045_region": CapacitySquare2045RegionChart,
    "energy_statusquo_region": EnergyRegionChart,
    "energy_2045_region": Energy2045RegionChart,
    "energy_share_statusquo_region": EnergyShareRegionChart,
    "energy_capita_statusquo_region": EnergyCapitaRegionChart,
    "energy_square_statusquo_region": EnergySquareRegionChart,
    "wind_turbines_statusquo_region": WindTurbinesRegionChart,
    "wind_turbines_2045_region": WindTurbines2045RegionChart,
    "wind_turbines_square_statusquo_region": WindTurbinesSquareRegionChart,
    "wind_turbines_square_2045_region": WindTurbinesSquare2045RegionChart,
    "electricity_demand_statusquo_region": ElectricityDemandRegionChart,
    "electricity_demand_2045_region": ElectricityDemand2045RegionChart,
    "electricity_demand_capita_statusquo_region": ElectricityDemandCapitaRegionChart,
    "electricity_demand_capita_2045_region": ElectricityDemandCapita2045RegionChart,
    "heat_demand_statusquo_region": HeatDemandRegionChart,
    "heat_demand_2045_region": HeatDemand2045RegionChart,
    "heat_demand_capita_statusquo_region": HeatDemandCapitaRegionChart,
    "heat_demand_capita_2045_region": HeatDemandCapita2045RegionChart,
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
