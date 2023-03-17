from django.apps import AppConfig


class MapConfig(AppConfig):
    name = "digiplan.map"

    def ready(self):
        # pylint: disable=C0415
        from django_mapengine import mvt, registry

        # pylint: disable=C0415
        from . import models

        registry.mvt_registry.register(
            "municipality",
            [
                mvt.MVTLayer("municipality", models.Municipality.vector_tiles),
                mvt.MVTLayer("municipalitylabel", models.Municipality.label_tiles),
            ],
        )
        registry.mvt_registry.register("results", [mvt.MVTLayer("results", models.Municipality.vector_tiles)])

        registry.cluster_registry.register("wind", models.WindTurbine)
        registry.cluster_registry.register("pvroof", models.PVroof)
        registry.cluster_registry.register("pvground", models.PVground)
        registry.cluster_registry.register("hydro", models.Hydro)
        registry.cluster_registry.register("biomass", models.Biomass)
        registry.cluster_registry.register("combustion", models.Combustion)
