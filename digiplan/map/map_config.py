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
        legend.LegendLayer(_("GSGK"), _("Wind turbine layer"), layer_id="gsgk", color="#1A1A1A"),
        legend.LegendLayer(_("Storage"), _("Wind turbine layer"), layer_id="storage", color="#1A1A1A"),
    ],
    _("Settlements Infrastructure"): [
        legend.LegendLayer(_("Settlement 0m"), _("Aviation layer"), layer_id="settlement-0m"),
        legend.LegendLayer(_("Industry"), _("Aviation layer"), layer_id="industry"),
        legend.LegendLayer(_("Road"), _("Aviation layer"), layer_id="road_default"),
        legend.LegendLayer(_("Railway"), _("Aviation layer"), layer_id="railway"),
        legend.LegendLayer(_("Road Railway 500m"), _("Aviation layer"), layer_id="road_railway-500m_region"),
        legend.LegendLayer(_("Aviation"), _("Aviation layer"), layer_id="aviation"),
        legend.LegendLayer(_("Air Traffic"), _("Air traffic layer"), layer_id="air_traffic"),
        legend.LegendLayer(_("Military"), _("Aviation layer"), layer_id="military"),
        legend.LegendLayer(_("Grid"), _("Aviation layer"), layer_id="grid"),
    ],
    _("Nature Landscape"): [
        legend.LegendLayer(_("Nature Conservation Area"), _("layer info"), layer_id="nature_conservation_area"),
        legend.LegendLayer(
            _("Drinking Water Protection Area"),
            _("layer info"),
            layer_id="drinking_water_protection_area",
        ),
        legend.LegendLayer(_("Fauna Flora Habitat"), _("layer info"), layer_id="fauna_flora_habitat"),
        legend.LegendLayer(_("Special Protection Area"), _("layer info"), layer_id="special_protection_area"),
        legend.LegendLayer(_("Biosphere Reserve"), _("Biosphere Reserve layer"), layer_id="biosphere_reserve"),
        legend.LegendLayer(_("Forest"), _("layer info"), layer_id="forest"),
        legend.LegendLayer(_("Water"), _("layer info"), layer_id="water"),
        legend.LegendLayer(_("Floodplain"), _("layer info"), layer_id="floodplain"),
        legend.LegendLayer(_("Landscape Protection Area"), _("layer info"), layer_id="landscape_protection_area"),
        legend.LegendLayer(_("Soil Quality High"), _("layer info"), layer_id="soil_quality_high"),
        legend.LegendLayer(_("Soil Quality Low"), _("layer info"), layer_id="soil_quality_low"),
    ],
}
