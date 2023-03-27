import math
import os

import pandas

from config.settings.base import DATA_DIR
from digiplan.map.models import (
    Biomass,
    Combustion,
    Hydro,
    Municipality,
    Population,
    PVground,
    PVroof,
    Region,
    WindTurbine,
)
from digiplan.utils.ogr_layer_mapping import RelatedModelLayerMapping

REGIONS = [Municipality]

MODELS = [WindTurbine, PVroof, PVground, Hydro, Biomass, Combustion]


def load_regions(regions=None, verbose=True):
    regions = regions or REGIONS
    for region in regions:
        if region.objects.exists():
            print(f"Skipping data for model '{region.__name__}' - Please empty model first if you want to update data.")
            continue
        print(f"Upload data for region '{region.__name__}'")
        if hasattr(region, "data_folder"):
            data_path = os.path.join(DATA_DIR, region.data_folder, f"{region.data_file}.gpkg")
        else:
            data_path = os.path.join(DATA_DIR, f"{region.data_file}.gpkg")
        region_model = Region(layer_type=region.__name__.lower())
        region_model.save()
        instance = RelatedModelLayerMapping(
            model=region,
            data=data_path,
            mapping=region.mapping,
            layer=region.layer,
            transform=4326,
        )
        instance.region = region_model
        instance.save(strict=True, verbose=verbose)


def load_data(models=None):
    models = models or MODELS
    for model in models:
        if model.objects.exists():
            print(f"Skipping data for model '{model.__name__}' - Please empty model first if you want to update data.")
            continue
        print(f"Upload data for model '{model.__name__}'")
        if hasattr(model, "data_folder"):
            data_path = os.path.join(DATA_DIR, model.data_folder, f"{model.data_file}.gpkg")
        else:
            data_path = os.path.join(DATA_DIR, f"{model.data_file}.gpkg")
        instance = RelatedModelLayerMapping(
            model=model,
            data=data_path,
            mapping=model.mapping,
            layer=model.layer,
            transform=4326,
        )
        instance.save(strict=True)


def load_population():
    filename = "population.csv"

    path = os.path.join(DATA_DIR, filename)
    municipalities = Municipality.objects.all()
    dataframe = pandas.read_csv(path, header=[0, 1], index_col=0)
    years = dataframe.columns.get_level_values(0)

    for municipality in municipalities:
        for year in years:
            series = dataframe.loc[municipality.id, year]

            value = list(series.values)[0]
            if math.isnan(value):
                continue

            entry = Population(
                year=year,
                value=value,
                entry_type=list(series.index.values)[0],
                municipality=municipality,
            )
            entry.save()


def empty_data(models=None):
    models = models or MODELS
    for model in models:
        model.objects.all().delete()
