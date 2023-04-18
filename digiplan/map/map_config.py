"""Actual map setup is done here."""

from django.utils.translation import gettext_lazy as _
from django_mapengine import legend

LEGEND = {
    _("Renewables"): [
        legend.LegendLayer(_("Wind turbine"), "", layer_id="wind", color="blue"),
        legend.LegendLayer(_("Roof-mounted PV"), "", layer_id="pvroof", color="yellow"),
        legend.LegendLayer(_("Outdoor PV"), "", layer_id="pvground", color="#F6B93B"),
        legend.LegendLayer(_("Hydro"), "", layer_id="hydro", color="#9CC4D9"),
        legend.LegendLayer(_("Biomass"), "", layer_id="biomass"),
        legend.LegendLayer(_("Combustion"), "", layer_id="combustion"),
    ],
}
