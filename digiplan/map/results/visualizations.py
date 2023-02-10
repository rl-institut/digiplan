from django.utils.translation import gettext as _
from oemoflex.postprocessing import core as results_core
from oemoflex.postprocessing import postprocessing

from digiplan.map.results import core


class TotalCosts(core.Visualization):
    name = "total_system_costs"
    title = _("Total Costs")
    calculation = postprocessing.TotalSystemCosts

    def _render(self):
        return {
            "lookup": self.name,
            "series": [
                {
                    "name": None,
                    "data": [
                        {"key": self.handler.scenarios[scenario_index].name, "value": result.sum().sum()}
                        for scenario_index, result in enumerate(self._result)
                    ],
                }
            ],
            "title": self.title,
        }


class Demand(core.Visualization):
    name = "demand"
    title = _("Demand")
    calculation = results_core.ParametrizedCalculation(
        postprocessing.AggregatedFlows,
        {
            "to_nodes": [
                "ABW-ch4-demand",
                "ABW-electricity-demand",
                "ABW-heat_central-demand",
                "ABW-heat_decentral-demand",
                "ABW-lignite-demand",
                "ABW-wood-demand",
            ]
        },
    )

    def _render(self):
        return {
            "lookup": self.name,
            "series": [
                {
                    "name": None,
                    "data": [
                        {"key": self.handler.scenarios[scenario_index].name, "value": result.sum()}
                        for scenario_index, result in enumerate(self._result)
                    ],
                }
            ],
            "title": self.title,
        }
