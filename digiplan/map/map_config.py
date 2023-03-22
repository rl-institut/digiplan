"""Actual map setup is done here."""

from django_mapengine import legend

LEGEND = {
    "Renewables": [
        legend.LegendLayer("Windturbinen", "", layer_id="wind", color="blue"),
        legend.LegendLayer("Aufdach-PV", "", layer_id="pvroof", color="yellow"),
        legend.LegendLayer("Boden-PV", "", layer_id="pvground"),
        legend.LegendLayer("Hydro", "", layer_id="hydro"),
        legend.LegendLayer("Biomasse", "", layer_id="biomass"),
        legend.LegendLayer("Fossile Kraftwerke", "", layer_id="combustion"),
    ],
}
