"""Module to test oemof simulation results."""
import os

import pandas as pd
from django.test import SimpleTestCase
from django_oemof import models
from django_oemof import results as oemof_results
from django_oemof import simulation

from digiplan.map import calculations, charts


class SimulationTest(SimpleTestCase):
    """Base class for simulation tests."""

    databases = ("default",)  # Needed, as otherwise django complains about tests using "default" DB
    parameters = {
        "s_v_1": None,
        "s_v_3": 100,
        "s_v_4": 100,
        "s_v_5": 100,
        "s_w_1": 1000,
        "w_v_1": None,
        "w_v_3": 100,
        "w_v_4": 100,
        "w_v_5": 100,
        "s_pv_ff_1": 100,
        "s_pv_d_1": 100,
        "s_h_1": 100,
        "s_s_g_1": 100,
        "w_d_wp_3": 100,
        "w_d_wp_4": 100,
        "w_d_wp_5": 100,
        "w_d_s_1": 50,
        "w_z_s_1": 53,
        "w_d_wp_1": True,
        "w_z_wp_1": None,
        "s_w_3": False,
        "s_w_4": True,
        "s_w_4_1": True,
        "s_w_4_2": True,
        "s_w_5": False,
        "s_w_5_1": 50,
        "s_w_5_2": 50,
        "s_pv_ff_3": 50,
        "s_pv_ff_4": 50,
        "s_pv_d_3": 50,
        "s_pv_d_4": 50,
    }

    def setUp(self) -> None:
        """Starts/loads oemof simulation for given parameters."""
        self.simulation_id = simulation.simulate_scenario("scenario_2045", self.parameters)
        if os.environ.get("TEST_SHOW_SIMULATION_RESULTS", "False") == "True":
            self.results = models.Simulation.objects.get(pk=self.simulation_id).dataset.restore_results()

    def tearDown(self) -> None:  # noqa: D102 Needed to keep results in test DB
        pass

    @classmethod
    def tearDownClass(cls):  # noqa: D102, ANN206 Needed to keep results in test DB
        pass


class EnergySharePerMunicipalityTest(SimpleTestCase):
    """Test energy shares per municipality calculation."""

    databases = ("default",)

    def test_energy_shares_per_municipality(self):  # noqa: D102
        results = calculations.energy_shares_per_municipality()
        assert len(results) == 20


class ElectricityDemandPerMunicipalityTest(SimpleTestCase):
    """Test electricity demand per municipality calculation."""

    databases = ("default",)

    def test_electricity_demand_per_municipality(self):  # noqa: D102
        results = calculations.electricity_demand_per_municipality()
        assert len(results) == 20
        assert len(results.columns) == 3


class HeatDemandPerMunicipalityTest(SimpleTestCase):
    """Test heat demand per municipality calculation."""

    databases = ("default",)

    def test_heat_demand_per_municipality(self):  # noqa: D102
        results = calculations.heat_demand_per_municipality()
        assert len(results) == 20
        assert len(results.columns) == 3


class PotentialShareTest(SimpleTestCase):
    """Test disaggregation of renewable potentials."""

    def test_potential_share(self):
        """Test renewable capacities."""
        parameters = {
            "s_w_3": True,
            "s_pv_ff_3": 50,
            "s_pv_ff_4": 50,
        }
        calculations.calculate_potential_shares(parameters)
        # assert results.sum() almost [1,1,1,1]


class ElectricityProductionTest(SimulationTest):
    """Test electricity production calculation."""

    def test_electricity_production(self):  # noqa: D102
        results = oemof_results.get_results(
            self.simulation_id,
            calculations=[calculations.electricity_production],
        )
        assert list(results.values())[0].iloc[0] > 0


class Energies2045Test(SimulationTest):
    """Test electricity production calculation."""

    def test_electricity_production(self):  # noqa: D102
        calculations.energies_per_municipality_2045(self.simulation_id)


class Capacities2045Test(SimulationTest):
    """Test electricity production calculation."""

    def test_capacities_2045(self):  # noqa: D102
        calculations.capacities_per_municipality_2045(self.simulation_id)


class WindTurbines2045Test(SimulationTest):
    """Test wind turbine calculation."""

    def test_wind_turbines_2045(self):  # noqa: D102
        result = calculations.wind_turbines_per_municipality_2045(self.simulation_id)
        assert len(result) == 20


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
        assert list(results.values())[0].iloc[1] > 0


class ElectricityDemand2045Test(SimulationTest):
    """Test electricity demand calculation."""

    def test_electricity_demand(self):  # noqa: D102
        results = calculations.electricity_demand_per_municipality_2045(self.simulation_id)
        assert len(results) == 20
        assert len(results.columns) == 4


class HeatDemandTest(SimulationTest):
    """Test heat demand calculation."""

    def test_heat_demand(self):  # noqa: D102
        results = oemof_results.get_results(
            self.simulation_id,
            calculations=[calculations.heat_demand],
        )
        assert list(results.values())[0].iloc[0] > 0


class HeatDemand2045Test(SimulationTest):
    """Test heat demand calculation in 2045."""

    def test_electricity_demand(self):  # noqa: D102
        results = calculations.heat_demand_per_municipality_2045(self.simulation_id)
        assert len(results) == 20
        assert len(results.columns) == 3


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


class MunicipalityTest(SimpleTestCase):
    """Test."""

    databases = ("default",)

    def test_square(self):
        """Test."""
        series = pd.Series([1, 2, 3], index=["a", "b", "c"])
        calculations.value_per_municipality(series)


class HeatStructureTest(SimulationTest):
    """Test heat overview calculation."""

    def test_heat_overview(self):  # noqa: D102
        result = calculations.heat_overview(self.simulation_id)
        assert len(result) == 3


class ElectricityOverviewChartTest(SimulationTest):
    """Test electricity overview chart creation."""

    def test_electricity_overview_chart(self):  # noqa: D102
        chart = charts.ElectricityOverviewChart(self.simulation_id)
        options = chart.render()
        assert options["series"][0]["data"][2] == 4369687.261432747


class HeatStructureChartTest(SimulationTest):
    """Test heat overview chart creation."""

    def test_heat_overview_chart(self):  # noqa: D102
        chart = charts.HeatStructureChart(self.simulation_id)
        options = chart.render()
        assert options["series"][0]["data"][1] == 3512007725.957367


class CapacityTest(SimulationTest):
    """Test reading capacities from oemof parameters."""

    def test_oemof_capacities(self):
        """Test capacity reading from oemof results."""
        results = oemof_results.get_results(self.simulation_id, {"capacities": calculations.Capacities})
        assert results["capacities"].loc["ABW-wind-onshore", "None"] == 1000.0
