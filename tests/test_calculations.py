from django.test import SimpleTestCase
from django_oemof import results as oemof_results
from django_oemof import simulation
from oemof.tabular.postprocessing import calculations as tabular_calculations
from oemof.tabular.postprocessing import core


class RenewableElectricityProductionTest(SimpleTestCase):
    databases = ("default",)  # Needed, as otherwise django complains about tests using "default" DB

    def tearDown(self) -> None:  # Needed to keep results in test DB
        pass

    @classmethod
    def tearDownClass(cls):  # Needed to keep results in test DB
        pass

    def test_renewable_electricity_production(self):
        calculation = core.ParametrizedCalculation(
            tabular_calculations.AggregatedFlows,
            {
                "from_nodes": [
                    "ABW-solar-pv_ground",
                ]
            },
        )
        parameters = {
            "s_v_2": 100,
            "s_v_3": 100,
            "s_v_4": 100,
            "s_w_1": 1000,
            "s_pv_ff_1": 300,
            "s_pv_d_1": 200,
            "s_b_1": 1000,
        }
        simulation_id = simulation.simulate_scenario("scenario_2045", parameters)
        results = oemof_results.get_results(simulation_id, calculations=[calculation])
        assert list(results.values())[0].iloc[0] > 0
