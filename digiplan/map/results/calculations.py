import json

from django.db.models import Sum

from config.settings.base import APPS_DIR

from .. import models


def installed_ee(input_mun_id):
    sums = []
    sum_wind = (
        models.WindTurbine.objects.all()
        .filter(mun_id__exact=input_mun_id)
        .aggregate(Sum("capacity_net"))["capacity_net__sum"]
    )
    sums.append(sum_wind)
    sum_pvground = (
        models.PVground.objects.all()
        .filter(mun_id__exact=input_mun_id)
        .aggregate(Sum("capacity_net"))["capacity_net__sum"]
    )
    sums.append(sum_pvground)
    sum_pvroof = (
        models.PVroof.objects.all()
        .filter(mun_id__exact=input_mun_id)
        .aggregate(Sum("capacity_net"))["capacity_net__sum"]
    )
    sums.append(sum_pvroof)
    sum_biomass = (
        models.Biomass.objects.all()
        .filter(mun_id__exact=input_mun_id)
        .aggregate(Sum("capacity_net"))["capacity_net__sum"]
    )
    sums.append(sum_biomass)
    sum_combustion = (
        models.Combustion.objects.all()
        .filter(mun_id__exact=input_mun_id)
        .aggregate(Sum("capacity_net"))["capacity_net__sum"]
    )
    sums.append(sum_combustion)
    sum_hydro = (
        models.Hydro.objects.all()
        .filter(mun_id__exact=input_mun_id)
        .aggregate(Sum("capacity_net"))["capacity_net__sum"]
    )
    sums.append(sum_hydro)

    sum_installed_ee = 0
    for value in sums:
        if value:
            sum_installed_ee = value + sum_installed_ee

    return round(sum_installed_ee, ndigits=2)


def installed_ee_region():
    sums = []
    sum_wind = models.WindTurbine.objects.only("capacity_net").aggregate(Sum("capacity_net"))["capacity_net__sum"]
    sums.append(sum_wind)
    sum_pvground = models.PVground.objects.only("capacity_net").aggregate(Sum("capacity_net"))["capacity_net__sum"]
    sums.append(sum_pvground)
    sum_pvroof = models.PVroof.objects.only("capacity_net").aggregate(Sum("capacity_net"))["capacity_net__sum"]
    sums.append(sum_pvroof)
    sum_biomass = models.Biomass.objects.only("capacity_net").aggregate(Sum("capacity_net"))["capacity_net__sum"]
    sums.append(sum_biomass)
    sum_combustion = models.Combustion.objects.only("capacity_net").aggregate(Sum("capacity_net"))["capacity_net__sum"]
    sums.append(sum_combustion)
    sum_hydro = models.Hydro.objects.only("capacity_net").aggregate(Sum("capacity_net"))["capacity_net__sum"]
    sums.append(sum_hydro)

    sum_installed_ee = 0
    for value in sums:
        if value:
            sum_installed_ee = value + sum_installed_ee
        print(sum_installed_ee)

    return round(sum_installed_ee, ndigits=2)


def write_in_file(mun_id):
    with open(
        APPS_DIR.path("map").path("results").path("templates").path("installed_ee.json"), "r", encoding="utf-8"
    ) as jsonFile:
        data = json.load(jsonFile)

    data["id"] = mun_id
    data["keyValues"]["region_value"] = installed_ee_region()
    data["keyValues"]["municipality_value"] = installed_ee(mun_id)

    with open(
        APPS_DIR.path("map").path("results").path("templates").path("installed_ee.json"), "w", encoding="utf-8"
    ) as jsonFile:
        json.dump(data, jsonFile)
