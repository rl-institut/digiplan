"""Module for calculations used for choropleths or charts."""

import json
import pathlib
from collections import namedtuple
from typing import Optional

import jsonschema
from django.db.models import Sum

from config import schemas
from digiplan.map import models
from digiplan.map.config import config

LookupFunctions = namedtuple("PopupData", ("data_fct", "chart_fct"))


def create_chart(lookup: str, municipality_id: int) -> dict:
    """Create chart based on given lookup and municipality ID.

    Parameters
    ----------
    lookup: str
        Looks up related chart function in LOOKUPS.
    municipality_id: int
        Used to calculate chart data related to given municipality.

    Returns
    -------
    dict
        Containing validated chart options for further use in JS
    """
    with pathlib.Path(config.POPUPS_DIR.path(f"{lookup}_chart.json")).open("r", encoding="utf-8") as chart_json:
        chart = json.load(chart_json)
    chart = LOOKUPS[lookup].chart_fct(chart, municipality_id)
    jsonschema.validate(chart, schemas.CHART_SCHEMA)
    return chart


def create_data(lookup: str, municipality_id: int) -> dict:
    """Create data for given lookup.

    Parameters
    ----------
    lookup: str
        Looks up related data function in LOOKUPS.
    municipality_id: int
        Used to calculate data related to given municipality.

    Returns
    -------
    dict
        containing popup data for given lookup
    """
    with pathlib.Path(config.POPUPS_DIR.path(f"{lookup}.json")).open("r", encoding="utf-8") as data_json:
        data = json.load(data_json)

    data["id"] = municipality_id
    data["data"]["region_value"] = LOOKUPS[lookup].data_fct()
    data["data"]["municipality_value"] = LOOKUPS[lookup].data_fct(municipality_id)

    return data


def get_data_for_installed_ee(municipality_id: Optional[int] = None) -> float:
    """Calculate installed renewables (either for municipality or for whole region).

    Parameters
    ----------
    municipality_id: Optional[int]
        If given, installed renewables for given municipality are calculated. If not, for whole region.

    Returns
    -------
    float
        Sum of installed renewables
    """
    installed_ee = 0.0
    for renewable in models.RENEWABLES:
        if municipality_id:
            res_installed_ee = renewable.objects.filter(mun_id__exact=municipality_id).aggregate(Sum("capacity_net"))[
                "capacity_net__sum"
            ]
        else:
            res_installed_ee = renewable.objects.aggregate(Sum("capacity_net"))["capacity_net__sum"]
        if res_installed_ee:
            installed_ee += res_installed_ee
    return installed_ee


# pylint: disable=W0613
def get_chart_for_installed_ee(chart: dict, municipality_id: int) -> dict:  # noqa: ARG001
    """Get chart for installed renewables.

    Parameters
    ----------
    chart: dict
        Default chart options for installed renewables from JSON
    municipality_id: int
        Related municipality

    Returns
    -------
    dict
        Chart data to use in JS
    """
    chart["series"][0]["data"] = [{"key": 2023, "value": 2}, {"key": 2045, "value": 3}, {"key": 2050, "value": 4}]
    return chart


LOOKUPS: dict[str, LookupFunctions] = {
    "installed_ee": LookupFunctions(get_data_for_installed_ee, get_chart_for_installed_ee),
}
