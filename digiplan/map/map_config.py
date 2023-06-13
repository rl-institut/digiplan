"""Actual map setup is done here."""

from django.utils.translation import gettext_lazy as _
from django_mapengine import legend

# TODO(Josi): Add real descriptions for layer info buttons
# https://github.com/rl-institut-private/digiplan/issues/249
LEGEND = {
    _("Renewables"): [
        legend.LegendLayer(_("Wind turbine"), _("Wind turbine layer"), layer_id="wind", color="#6A89CC"),
        legend.LegendLayer(_("Roof-mounted PV"), _("PV roof layer"), layer_id="pvroof", color="#FFD660"),
        legend.LegendLayer(_("Outdoor PV"), _("Hydro layer"), layer_id="pvground", color="#F6B93B"),
        legend.LegendLayer(_("Hydro"), _("Hydro layer"), layer_id="hydro", color="#9CC4D9"),
        legend.LegendLayer(_("Biomass"), _("Wind turbine layer"), layer_id="biomass", color="#52C41A"),
        legend.LegendLayer(_("Combustion"), _("Wind turbine layer"), layer_id="combustion", color="#1A1A1A"),
    ],
}
