"""Module to test oemof simulation results."""

from django.test import SimpleTestCase
from django_oemof import results as oemof_results
from django_oemof import simulation

from digiplan.map import calculations


class RenewableElectricityProductionTest(SimpleTestCase):
    """Test renewable electricity production calculation."""

    databases = ("default",)  # Needed, as otherwise django complains about tests using "default" DB

    def tearDown(self) -> None:  # noqa: D102 Needed to keep results in test DB
        pass

    @classmethod
    def tearDownClass(cls):  # noqa: D102,ANN102,ANN206 Needed to keep results in test DB
        pass

    def test_renewable_electricity_production(self):  # noqa: D102,ANN201
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
        results = oemof_results.get_results(simulation_id, calculations=[calculations.renewable_electricity_production])
        assert list(results.values())[0].iloc[0] > 0
