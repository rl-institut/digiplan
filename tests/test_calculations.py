"""Module to test oemof simulation results."""

from django.test import SimpleTestCase
from django_oemof import results as oemof_results
from django_oemof import simulation

from digiplan.map import calculations, charts


class SimulationTest(SimpleTestCase):
    """Base class for simulation tests."""

    databases = ("default",)  # Needed, as otherwise django complains about tests using "default" DB
    parameters = {
        "s_v_2": 100,
        "s_v_3": 100,
        "s_v_4": 100,
        "s_w_1": 1000,
        "w_v_3": 100,
        "w_v_4": 100,
        "w_v_5": 100,
        "s_pv_ff_1": 100,
        "s_pv_d_1": 100,
        "s_b_1": 100,
        "ror": 100,
        "w_z_wp_1": 100,
        "w_d_wp_1": 100,
    }

    def setUp(self) -> None:
        """Starts/loads oemof simulation for given parameters."""
        self.simulation_id = simulation.simulate_scenario("scenario_2045", self.parameters)

    def tearDown(self) -> None:  # noqa: D102 Needed to keep results in test DB
        pass

    @classmethod
    def tearDownClass(cls):  # noqa: D102, ANN206 Needed to keep results in test DB
        pass


class ElectricityProductionTest(SimulationTest):
    """Test electricity production calculation."""

    def test_electricity_production(self):  # noqa: D102
        results = oemof_results.get_results(
            self.simulation_id,
            calculations=[calculations.electricity_production],
        )
        assert list(results.values())[0].iloc[0] > 0


class HeatProductionTest(SimulationTest):
    """Test heat production calculation."""

    def test_heat_production(self):  # noqa: D102
        results = oemof_results.get_results(
            self.simulation_id,
            calculations=[calculations.heat_production],
        )
        assert list(results.values())[0].iloc[0] > 0


class ElectricityDemandTest(SimulationTest):
    """Test electricity demand calculation."""

    def test_electricity_demand(self):  # noqa: D102
        results = oemof_results.get_results(
            self.simulation_id,
            calculations=[calculations.electricity_demand],
        )
        assert list(results.values())[0].iloc[0] > 0


class HeatDemandTest(SimulationTest):
    """Test heat demand calculation."""

    def test_heat_demand(self):  # noqa: D102
        results = oemof_results.get_results(
            self.simulation_id,
            calculations=[calculations.heat_demand],
        )
        assert list(results.values())[0].iloc[0] > 0


class ElectricityProductionFromBiomassTest(SimulationTest):
    """Test electricity production from biomass calculation."""

    def test_electricity_production_from_biomass(self):  # noqa: D102
        results = calculations.electricity_from_from_biomass(self.simulation_id)
        assert isinstance(results, float) is True


class ElectricityOverviewTest(SimulationTest):
    """Test electricity overview calculation."""

    def test_electricity_overview(self):  # noqa: D102
        result = calculations.electricity_overview(self.simulation_id)
        assert len(result) == 12


class HeatOverviewTest(SimulationTest):
    """Test heat overview calculation."""

    def test_heat_overview(self):  # noqa: D102
        result = calculations.heat_overview(self.simulation_id)
        assert len(result) == 3


class ElectricityOverviewChartTest(SimulationTest):
    """Test electricity overview chart creation."""

    def test_electricity_overview_chart(self):  # noqa: D102,ANN201
        chart = charts.ElectricityOverviewChart(self.simulation_id)
        options = chart.render()
        assert options["series"][0]["data"][2] == 4369687.261432747


class HeatOverviewChartTest(SimulationTest):
    """Test heat overview chart creation."""

    def test_heat_overview_chart(self):  # noqa: D102,ANN201
        chart = charts.HeatOverviewChart(self.simulation_id)
        options = chart.render()
        assert options["series"][0]["data"][1] == 3512007725.957367
