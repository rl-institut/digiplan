from django.utils.translation import gettext as _
from oemof.tabular.postprocessing import calculations
from oemof.tabular.postprocessing import core as results_core

from digiplan.map.results import core


class TotalCosts(core.Visualization):
    name = "total_system_costs"
    title = _("Total Costs")
    calculation = calculations.TotalSystemCosts

    def _render(self):
        return {
            "lookup": self.name,
            "series": [
                {
                    "name": None,
                    "data": [
                        {"key": self.get_scenario_name(scenario_index), "value": result.sum().sum()}
                        for scenario_index, result in enumerate(self._result)
                    ],
                }
            ],
            "title": self.title,
        }


class ElectricityDemand(core.Visualization):
    name = "electricity_demand"
    title = _("Electricity Demand")
    calculation = results_core.ParametrizedCalculation(
        calculations.AggregatedFlows,
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
                        {"key": self.get_scenario_name(scenario_index), "value": result.sum()}
                        for scenario_index, result in enumerate(self._result)
                    ],
                }
            ],
            "title": self.title,
        }


class RenewableElectricityProduction(core.Visualization):
    name = "renewable_electricity_production"
    title = _("Renewable Electricity Production")
    calculation = results_core.ParametrizedCalculation(
        calculations.AggregatedFlows,
        {
            "from_nodes": [
                "ABW-solar-pv_ground",
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
                        {"key": self.get_scenario_name(scenario_index), "value": result.sum()}
                        for scenario_index, result in enumerate(self._result)
                    ],
                }
            ],
            "title": self.title,
        }
