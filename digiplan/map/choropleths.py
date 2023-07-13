"""Module to support choropleths in digiplan."""

import abc
from collections.abc import Callable
from typing import Optional, Union

import pandas as pd
from django.conf import settings
from django.http.response import JsonResponse

from . import calculations, models


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
        return JsonResponse({"values": values, "paintProperties": paint_properties})


class EnergyShareChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return calculations.energy_shares_per_municipality().sum(axis=1).to_dict()


class EnergyChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return calculations.energies_per_municipality().sum(axis=1).to_dict()


class Energy2045Choropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return calculations.energies_per_municipality_2045(self.map_state["simulation_id"]).sum(axis=1).to_dict()


class EnergyCapitaChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        energies = calculations.energies_per_municipality()
        energies_per_capita = calculations.calculate_capita_for_value(energies) * 1e3
        return energies_per_capita.sum(axis=1).to_dict()


class EnergyCapita2045Choropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        energies = calculations.energies_per_municipality_2045(self.map_state["simulation_id"])
        energies_per_capita = calculations.calculate_capita_for_value(energies) * 1e3
        return energies_per_capita.sum(axis=1).to_dict()


class EnergySquareChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        energies = calculations.energies_per_municipality()
        energies_per_square = calculations.calculate_square_for_value(energies) * 1e3
        return energies_per_square.sum(axis=1).to_dict()


class EnergySquare2045Choropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        energies = calculations.energies_per_municipality_2045(self.map_state["simulation_id"])
        energies_per_square = calculations.calculate_square_for_value(energies) * 1e3
        return energies_per_square.sum(axis=1).to_dict()


class CapacityChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> pd.DataFrame:  # noqa: D102
        capacities = calculations.capacities_per_municipality().sum(axis=1)
        return capacities.to_dict()


class CapacitySquareChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        capacities = calculations.capacities_per_municipality()
        capacities_square = calculations.calculate_square_for_value(capacities)
        return capacities_square.sum(axis=1).to_dict()


class PopulationChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return models.Population.quantity_per_municipality_per_year().sum(axis=1).to_dict()


class PopulationDensityChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        population = models.Population.quantity_per_municipality_per_year()
        population_square = calculations.calculate_square_for_value(population)
        return population_square.sum(axis=1).to_dict()


class EmployeesChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return calculations.employment_per_municipality().to_dict()


class CompaniesChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return calculations.companies_per_municipality().to_dict()


class WindTurbinesChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return models.WindTurbine.quantity_per_municipality().to_dict()


class WindTurbinesSquareChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        wind_turbines = models.WindTurbine.quantity_per_municipality()
        wind_turbines_square = calculations.calculate_square_for_value(wind_turbines)
        return wind_turbines_square.to_dict()


class ElectricityDemandChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return calculations.electricity_demand_per_municipality().sum(axis=1).to_dict()


class ElectricityDemandCapitaChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return (
            calculations.calculate_capita_for_value(calculations.electricity_demand_per_municipality())
            .sum(axis=1)
            .to_dict()
        )


class HeatDemandChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return calculations.heat_demand_per_municipality().sum(axis=1).to_dict()


class HeatDemandCapitaChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return (
            calculations.calculate_capita_for_value(calculations.heat_demand_per_municipality()).sum(axis=1).to_dict()
        )


class BatteriesChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return calculations.batteries_per_municipality().to_dict()


class BatteriesCapacityChoropleth(Choropleth):  # noqa: D101
    def get_values_per_feature(self) -> dict[int, float]:  # noqa: D102
        return calculations.battery_capacities_per_municipality().to_dict()


CHOROPLETHS: dict[str, Union[Callable, type(Choropleth)]] = {
    "population_statusquo": PopulationChoropleth,
    "population_density_statusquo": PopulationDensityChoropleth,
    "employees_statusquo": EmployeesChoropleth,
    "companies_statusquo": CompaniesChoropleth,
    "energy_statusquo": EnergyChoropleth,
    "energy_2045": Energy2045Choropleth,
    "energy_share_statusquo": EnergyShareChoropleth,
    "energy_capita_statusquo": EnergyCapitaChoropleth,
    "energy_capita_2045": EnergyCapita2045Choropleth,
    "energy_square_statusquo": EnergySquareChoropleth,
    "energy_square_2045": EnergySquare2045Choropleth,
    "capacity_statusquo": CapacityChoropleth,
    "capacity_square_statusquo": CapacitySquareChoropleth,
    "wind_turbines_statusquo": WindTurbinesChoropleth,
    "wind_turbines_square_statusquo": WindTurbinesSquareChoropleth,
    "electricity_demand_statusquo": ElectricityDemandChoropleth,
    "electricity_demand_capita_statusquo": ElectricityDemandCapitaChoropleth,
    "heat_demand_statusquo": HeatDemandChoropleth,
    "heat_demand_capita_statusquo": HeatDemandCapitaChoropleth,
    "batteries_statusquo": BatteriesChoropleth,
    "batteries_capacity_statusquo": BatteriesCapacityChoropleth,
}
