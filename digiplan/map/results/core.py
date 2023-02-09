import abc
from collections import namedtuple
from typing import List, Type, Union

import jsonschema
from django.conf import settings
from django_oemof.results import CALCULATIONS, get_results
from oemoflex.postprocessing import core

from config.schemas import CHART_SCHEMA

Scenario = namedtuple("Scenario", ["name", "parameters"])

VISUALIZATIONS = {}


def add_visualization(visualization):
    VISUALIZATIONS[visualization.name] = visualization


class VisualizationError(Exception):
    """Raised if visualization goes wrong."""


class VisualizationHandler:
    def __init__(self, scenarios: List[Scenario]):
        self.scenarios: List[Scenario] = scenarios
        self.visualizations = {}
        self.results = []

    def add(self, visualization):
        if visualization not in VISUALIZATIONS:
            if settings.DEBUG and visualization in CALCULATIONS:
                self.visualizations[visualization] = DefaultVisualization(
                    self, visualization, CALCULATIONS[visualization]
                )
            else:
                raise VisualizationError(f"Could not find {visualization=}.")
        else:
            self.visualizations[visualization] = VISUALIZATIONS[visualization](self)

    def run(self):
        calculations = [
            core.get_dependency_name(visualization.calculation) for visualization in self.visualizations.values()
        ]
        for scenario in self.scenarios:
            self.results.append(
                get_results(scenario=scenario.name, parameters=scenario.parameters, calculations=calculations)
            )

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
        if not settings.DEBUG:
            self.validate(rendered)
        return rendered

    @abc.abstractmethod
    def _render(self):
        """Render method should be overwritten in child class and shall return a valid chart dict/JSON"""

    @staticmethod
    def validate(rendered):
        jsonschema.validate(rendered, CHART_SCHEMA)


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
                        {"key": self.handler.scenarios[scenario_index].name, "value": result.to_json()}
                        for scenario_index, result in enumerate(self._result)
                    ],
                }
            ],
            "title": self.title,
        }
