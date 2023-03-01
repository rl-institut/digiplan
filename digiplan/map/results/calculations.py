import json
from collections import namedtuple
from typing import Dict, Optional

import jsonschema
from django.db.models import Sum

from config import schemas
from digiplan.map import models
from digiplan.map.config import config

LookupFunctions = namedtuple("PopupData", ("data_fct", "chart_fct"))


def create_chart(lookup):
    with open(config.POPUPS_DIR.path(f"{lookup}_chart.json"), "r", encoding="utf-8") as chart_json:
        chart = json.load(chart_json)
    chart = LOOKUPS[lookup].chart_fct(chart)
    jsonschema.validate(chart, schemas.CHART_SCHEMA)
    return chart


def create_data(lookup, mun_id):
    with open(config.POPUPS_DIR.path(f"{lookup}.json"), "r", encoding="utf-8") as data_json:
        data = json.load(data_json)

    data["id"] = mun_id
    data["data"]["region_value"] = LOOKUPS[lookup].data_fct()
    data["data"]["municipality_value"] = LOOKUPS[lookup].data_fct(mun_id)

    return data


def get_data_for_installed_ee(municipality_id: Optional[int] = None):
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


def get_chart_for_installed_ee(chart):
    chart["series"][0]["data"] = [{"key": 2023, "value": 2}, {"key": 2045, "value": 3}, {"key": 2050, "value": 4}]
    return chart


LOOKUPS: Dict[str, LookupFunctions] = {
    "installed_ee": LookupFunctions(get_data_for_installed_ee, get_chart_for_installed_ee)
}
