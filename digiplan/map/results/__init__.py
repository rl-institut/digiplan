from django_oemof import results

from . import core, visualizations

core.add_visualization(visualizations.TotalCosts)
core.add_visualization(visualizations.ElectricityDemand)
core.add_visualization(visualizations.RenewableElectricityProduction)

for visualization in core.VISUALIZATIONS.values():
    results.register_calculation(visualization.calculation)
