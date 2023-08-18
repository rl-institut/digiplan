"""Actual map setup is done here."""
import dataclasses

from django.utils.translation import gettext_lazy as _
from django_mapengine import legend


@dataclasses.dataclass
class SymbolLegendLayer(legend.LegendLayer):
    """Adds symbol field."""

    symbol: str = "rectangle"


# TODO(Josi): Add real descriptions for layer info buttons
# https://github.com/rl-institut-private/digiplan/issues/249
LEGEND = {
    _("Renewables"): [
        SymbolLegendLayer(
            _("Wind turbine"),
            _("Windenergieanlagen: Installierte Leistung und Anzahl"),
            layer_id="wind",
            color="#6A89CC",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Roof-mounted PV"),
            _("PV-Aufdachanlagen: Installierte Leistung und Anzahl"),
            layer_id="pvroof",
            color="#FFD660",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Outdoor PV"),
            _("PV-Freiflächenanlagen: Installierte Leistung und Anzahl"),
            layer_id="pvground",
            color="#EFAD25",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Hydro"),
            _("Wasserkraftanlagen: Installierte Leistung und Anzahl"),
            layer_id="hydro",
            color="#A9BDE8",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Biomass"),
            _("Biomasseanlagen: Installierte Leistung und Anzahl"),
            layer_id="biomass",
            color="#52C41A",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Combustion"),
            _("Verbrennungskraftwerke: Installierte Leistung und Anzahl"),
            layer_id="combustion",
            color="#E6772E",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("GSGK"),
            _("Geo- oder Solarthermie-, Grubengas- und Klärschlamm-Anlagen: Installierte Leistung und Anzahl"),
            layer_id="gsgk",
            color="#C27BA0",
            symbol="circle",
        ),
        SymbolLegendLayer(
            _("Storage"),
            _("Batteriespeicher gesamt: Installierte Leistung und Anzahl"),
            layer_id="storage",
            color="#8D2D5F",
            symbol="circle",
        ),
    ],
    _("Settlements Infrastructure"): [
        legend.LegendLayer(_("Settlement 0m"), _("Siedlungen"), layer_id="settlement-0m"),
        legend.LegendLayer(_("Industry"), _("Industrie- und Gewerbegebiete"), layer_id="industry"),
        legend.LegendLayer(
            _("Road Railway 500m"),
            _("Straßen und Bahnverkehr (500 m Puffer)"),
            layer_id="road_railway-500m_region",
        ),
        legend.LegendLayer(_("Road"), _("Straßen"), layer_id="road_default"),
        legend.LegendLayer(_("Railway"), _("Bahnverkehr"), layer_id="railway"),
        legend.LegendLayer(_("Aviation"), _("Luftverkehr"), layer_id="aviation"),
        legend.LegendLayer(_("Air Traffic"), _("Drehfunkfeuer"), layer_id="air_traffic"),
        legend.LegendLayer(_("Military"), _("Militärische Sperrgebiete und Liegenschaften"), layer_id="military"),
        legend.LegendLayer(_("Grid"), _("Stromnetze (>=110 kV)"), layer_id="grid"),
    ],
    _("Nature Landscape"): [
        legend.LegendLayer(_("Nature Conservation Area"), _("Naturschutzgebiete"), layer_id="nature_conservation_area"),
        legend.LegendLayer(_("Fauna Flora Habitat"), _("Fauna-Flora-Habitate"), layer_id="fauna_flora_habitat"),
        legend.LegendLayer(_("Special Protection Area"), _("layer info"), layer_id="special_protection_area"),
        legend.LegendLayer(_("Biosphere Reserve"), _("Biosphärenreservate"), layer_id="biosphere_reserve"),
        legend.LegendLayer(
            _("Landscape Protection Area"),
            _("Landschaftsschutzgebiete"),
            layer_id="landscape_protection_area",
        ),
        legend.LegendLayer(_("Forest"), _("Wälder"), layer_id="forest"),
        legend.LegendLayer(
            _("Drinking Water Protection Area"),
            _("Wasserschutzgebiete"),
            layer_id="drinking_water_protection_area",
        ),
        legend.LegendLayer(_("Water"), _("Gewässer"), layer_id="water"),
        legend.LegendLayer(_("Floodplain"), _("Überschwemmungsgebiete"), layer_id="floodplain"),
        legend.LegendLayer(
            _("Soil Quality High"),
            _("Ackerflächen mit hoher Bodenqualität (Soil Quality Rating >= 40)"),
            layer_id="soil_quality_high",
        ),
        legend.LegendLayer(
            _("Soil Quality Low"),
            _("Ackerflächen mit geringer Bodenqualität (Soil Quality Rating < 40)"),
            layer_id="soil_quality_low",
        ),
    ],
}
