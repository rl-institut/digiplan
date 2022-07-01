from digiplan.map import models
from digiplan.map.mvt import MVTLayer

REGION_MVT_LAYERS = {
    "municipality": [
        MVTLayer("municipality", models.Municipality.vector_tiles),
        MVTLayer("municipalitylabel", models.Municipality.label_tiles),
    ],
}

STATIC_MVT_LAYERS = {
    "static": [],
}

DYNAMIC_MVT_LAYERS = {}

MVT_LAYERS = dict(**REGION_MVT_LAYERS, **STATIC_MVT_LAYERS, **DYNAMIC_MVT_LAYERS)
DISTILL_MVT_LAYERS = dict(**REGION_MVT_LAYERS, **STATIC_MVT_LAYERS)
