import json
from typing import Optional

from django.db.models import Sum

from digiplan.map.config import config

from .. import models


def calc_installed_ee(municipality_id: Optional[int] = None):
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


def create_chart(lookup):
    with open(config.POPUPS_DIR.path(lookup + "_chart.json"), "r", encoding="utf-8") as jsonFile:
        chart = json.load(jsonFile)

    return chart


def create_data(lookup, mun_id):
    with open(config.POPUPS_DIR.path(lookup + ".json"), "r", encoding="utf-8") as jsonFile:
        data = json.load(jsonFile)

    data["id"] = mun_id
    data["data"]["region_value"] = calc_installed_ee()
    data["data"]["municipality_value"] = calc_installed_ee(mun_id)

    return data
