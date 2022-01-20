from . import models
from .mvt import MVTLayer

REGION_MVT_LAYERS = {
    "country": [MVTLayer("country", models.Country.vector_tiles), MVTLayer("countrylabel", models.Country.label_tiles)],
    "state": [MVTLayer("state", models.State.vector_tiles), MVTLayer("statelabel", models.State.label_tiles)],
    "district": [
        MVTLayer("district", models.District.vector_tiles),
        MVTLayer("districtlabel", models.District.label_tiles),
    ],
}

STATIC_MVT_LAYERS = {
    "static": [
        MVTLayer("built_up_areas", models.BuiltUpAreas.vector_tiles),
        MVTLayer("settlements", models.Settlements.vector_tiles),
        MVTLayer("hamlets", models.Hamlets.vector_tiles),
        MVTLayer("nightlight", models.Nightlight.vector_tiles),
        MVTLayer("hospital_simulated", models.HospitalsSimulated.vector_tiles),
        MVTLayer("grid", models.Grid.vector_tiles),
    ],
    "hamlets": [MVTLayer("hamlets", models.Hamlets.vector_tiles)],
}

DYNAMIC_MVT_LAYERS = {}

MVT_LAYERS = dict(**REGION_MVT_LAYERS, **STATIC_MVT_LAYERS, **DYNAMIC_MVT_LAYERS)
DISTILL_MVT_LAYERS = dict(**REGION_MVT_LAYERS, **STATIC_MVT_LAYERS)
