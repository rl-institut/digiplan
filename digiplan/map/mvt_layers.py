from . import models
from .mvt import MVTLayer

REGION_MVT_LAYERS = {
    "municipality": [
        MVTLayer("municipality", models.Municipality.vector_tiles),
        MVTLayer("municipalitylabel", models.Municipality.label_tiles),
    ],
}

STATIC_MVT_LAYERS = {
    "static": [
        MVTLayer("results", models.WindTurbine.vector_tiles),
        MVTLayer("results", models.PVroof.vector_tiles),
        MVTLayer("results", models.PVground.vector_tiles),
    ],
    "results": [MVTLayer("results", models.Municipality.vector_tiles)],
}

DYNAMIC_MVT_LAYERS = {}

MVT_LAYERS = dict(**REGION_MVT_LAYERS, **STATIC_MVT_LAYERS, **DYNAMIC_MVT_LAYERS)
DISTILL_MVT_LAYERS = dict(**REGION_MVT_LAYERS, **STATIC_MVT_LAYERS)
