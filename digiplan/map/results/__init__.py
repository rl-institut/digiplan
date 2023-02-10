from django_oemof import results
from oemoflex.postprocessing import core as results_core
from oemoflex.postprocessing import postprocessing

from . import core, visualizations

results.register_calculation(
    results_core.ParametrizedCalculation(postprocessing.AggregatedFlows, {"to_nodes": ["demand"]})
)
core.add_visualization(visualizations.TotalCosts)
core.add_visualization(visualizations.Demand)
