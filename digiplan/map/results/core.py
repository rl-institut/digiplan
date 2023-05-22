import abc
from typing import List, Type, Union

from django.conf import settings
from django_oemof import models, results
from oemoflex.postprocessing import core

VISUALIZATIONS = {}


def add_visualization(visualization):
    VISUALIZATIONS[visualization.name] = visualization


class VisualizationError(Exception):
    """Raised if visualization goes wrong."""


class VisualizationHandler:
    def __init__(self, simulations: List[int]):
        self.simulations: List[int] = simulations
        self.visualizations = {}
        self.results = []

    def add(self, visualization):
        if visualization not in VISUALIZATIONS:
            if settings.DEBUG and visualization in results.CALCULATIONS:
                self.visualizations[visualization] = DefaultVisualization(
                    self, visualization, results.CALCULATIONS[visualization]
                )
            else:
                raise VisualizationError(f"Could not find {visualization=}.")
        else:
            self.visualizations[visualization] = VISUALIZATIONS[visualization](self)

    def run(self):
        calculations = [
            core.get_dependency_name(visualization.calculation) for visualization in self.visualizations.values()
        ]
        for simulation in self.simulations:
            self.results.append(results.get_results(simulation_id=simulation, calculations=calculations))

    def __getitem__(self, visualization_name):
        return self.visualizations[visualization_name].render()


class Visualization(abc.ABC):
    name: str = None
    title: str = None
    calculation: Union[Type[core.Calculation], core.ParametrizedCalculation] = None

    def __init__(self, visualization_handler: VisualizationHandler):
        self.handler = visualization_handler
        self._result = None

    def render(self):
        if not self._result:
            self._result = [result[core.get_dependency_name(self.calculation)] for result in self.handler.results]
        rendered = self._render()
        return rendered

    @abc.abstractmethod
    def _render(self):
        """Render method should be overwritten in child class and shall return a valid chart dict/JSON"""

    def get_scenario_name(self, simulation_index):
        return models.Simulation.objects.get(pk=self.handler.simulations[simulation_index]).scenario


class DefaultVisualization(Visualization):
    def __init__(
        self,
        visualization_handler: VisualizationHandler,
        name: str,
        calculation: Union[Type[core.Calculation], core.ParametrizedCalculation],
    ):
        super().__init__(visualization_handler)
        self.name = name
        self.title = name
        self.calculation = calculation

    def _render(self):
        # pylint: disable=R0801
        return {
            "lookup": self.name,
            "series": [
                {
                    "name": None,
                    "data": [
                        {"key": self.get_scenario_name(scenario_index), "value": result.to_json()}
                        for scenario_index, result in enumerate(self._result)
                    ],
                }
            ],
            "title": self.title,
        }
