"""Provide popups for digiplan."""

import abc
from collections import namedtuple
from collections.abc import Iterable
from typing import Optional, Union

import pandas as pd
from django.utils.translation import gettext_lazy as _
from django_mapengine import popups
from django_oemof import results
from oemof.tabular.postprocessing import core

from . import calculations, charts, config, models

Source = namedtuple("Source", ("name", "url"))


class RegionPopup(popups.ChartPopup):
    """Popup containing values for municipality and region in header."""

    title: str = None
    description: str = None
    unit: str = None
    sources: Optional[list[Source]] = None

    def __init__(
        self,
        lookup: str,
        selected_id: int,
        map_state: Optional[dict] = None,
        template: Optional[str] = None,
    ) -> None:
        """Initialize parent popup class and adds initialization of detailed data."""
        super().__init__(lookup, selected_id, map_state, template)
        self.detailed_data = self.get_detailed_data()

    def get_context_data(self) -> dict:
        """
        Set up context data including municipality and region values.

        Returns
        -------
        dict
            context dict including region and municipality data
        """
        return {
            "id": self.selected_id,
            "title": self.title,
            "description": self.description,
            "unit": self.unit,
            "region_value": self.get_region_value(),
            "municipality_value": self.get_municipality_value(),
            "municipality": models.Municipality.objects.get(pk=self.selected_id),
        }

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
    def get_detailed_data(self) -> pd.DataFrame:
        """
        Return detailed data for each municipality and technology/component.

        Municipality IDs are stored in index, components/technologies/etc. are stored in columns
        """

    def get_region_value(self) -> float:
        """Return aggregated data of all municipalities and technologies."""
        return self.detailed_data.sum().sum()

    def get_municipality_value(self) -> Optional[float]:
        """Return aggregated data for all technologies for given municipality ID."""
        if self.selected_id not in self.detailed_data.index:
            return 0
        return self.detailed_data.loc[self.selected_id].sum()

    def get_chart_data(self) -> Iterable:
        """Return data for given municipality ID."""
        if self.selected_id not in self.detailed_data.index:
            msg = "No chart data available for given ID"
            raise KeyError(msg)
        return self.detailed_data.loc[self.selected_id]


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
        return calculations.capacity()

    def get_municipality_value(self) -> float:  # noqa: D102
        return calculations.capacity(self.selected_id)

    def get_chart_data(self) -> Iterable:  # noqa: D102
        return calculations.capacity_comparison(self.selected_id)


class CapacitySquarePopup(RegionPopup):
    """Popup to show capacities per km²."""

    def get_region_value(self) -> float:  # noqa: D102
        return calculations.capacity_square

    def get_municipality_value(self) -> float:  # noqa: D102
        return calculations.capacity_square(self.selected_id)

    def get_chart_data(self) -> Iterable:  # noqa: D102
        return calculations.capacity_square_comparison(self.selected_id)


class PopulationPopup(RegionPopup):
    """Popup to show Population."""

    def get_region_value(self) -> float:  # noqa: D102
        return models.Population.quantity(2022)

    def get_municipality_value(self) -> float:  # noqa: D102
        return models.Population.quantity(2022, self.selected_id)

    def get_chart_data(self) -> Iterable:  # noqa: D102
        return models.Population.population_history(self.selected_id)


class PopulationDensityPopup(RegionPopup):
    """Popup to show Population Density."""

    def get_region_value(self) -> float:  # noqa: D102
        return models.Population.density(2022)

    def get_municipality_value(self) -> float:  # noqa: D102
        return models.Population.density(2022, self.selected_id)

    def get_chart_data(self) -> Iterable:  # noqa: D102
        return models.Population.density_history(self.selected_id)


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


class NumberWindturbinesPopup(RegionPopup):
    """Popup to show the number of wind turbines."""

    title = _("Number of wind turbines")
    description = _("Description for number of wind turbines")
    unit = ""

    def get_detailed_data(self) -> pd.DataFrame:
        """Return quantity of wind turbines per municipality (index)."""
        units_per_municipality = models.WindTurbine.quantity_per_municipality()
        return pd.DataFrame(units_per_municipality).set_index(0)

    def get_chart_data(self) -> Iterable:
        """Return single value for wind turbines in current municipality."""
        if self.selected_id not in self.detailed_data.index:
            return [0]
        return [int(self.detailed_data.loc[self.selected_id].iloc[0])]


class NumberWindturbinesSquarePopup(RegionPopup):
    """Popup to show the number of wind turbines per km²."""

    def get_region_value(self) -> float:  # noqa: D102
        return models.WindTurbine.quantity_per_square()

    def get_municipality_value(self) -> float:  # noqa: D102
        return models.WindTurbine.quantity_per_square(self.selected_id)

    def get_chart_data(self) -> Iterable:  # noqa: D102
        return models.WindTurbine.wind_turbines_per_area_history(self.selected_id)


POPUPS: dict[str, type(popups.Popup)] = {
    "capacity": CapacityPopup,
    "capacity_square": CapacitySquarePopup,
    "population": PopulationPopup,
    "population_density": PopulationDensityPopup,
    "renewable_electricity_production": RenewableElectricityProductionPopup,
    "wind_turbines": NumberWindturbinesPopup,
    "wind_turbines_square": NumberWindturbinesSquarePopup,
}
