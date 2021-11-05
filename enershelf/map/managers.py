from django.db import connection
from django.core.exceptions import FieldError
from rest_framework.serializers import ValidationError
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.geos import Polygon
from rest_framework_gis.tilenames import tile_edges

from enershelf.map.config import REGION_ZOOMS


class AsMVTGeom(models.functions.GeomOutputGeoFunc):
    function = "ST_AsMVTGeom"
    geom_param_pos = (0, 1)


class X(models.functions.Func):
    function = "ST_X"


class Y(models.functions.Func):
    function = "ST_Y"


class MVTManager(models.Manager):
    def __init__(self, *args, geo_col="geom", columns=None, **kwargs):
        super(MVTManager, self).__init__(*args, **kwargs)
        self.geo_col = geo_col
        self.columns = columns

    def get_mvt_query(self, x, y, z, filters=None):
        filters = filters or {}
        return self._build_mvt_query(x, y, z, filters)

    def get_columns(self):
        return self.columns or self._get_non_geom_columns()

    def _filter_query(self, query, x, y, z, filters):
        return query.filter(**filters)

    def _get_mvt_geom_query(self, x, y, z):
        bbox = Polygon.from_bbox(tile_edges(x, y, z))
        bbox.srid = 4326
        query = self.annotate(mvt_geom=AsMVTGeom(Transform(self.geo_col, 3857), Transform(bbox, 3857), 4096, 0, False))
        intersect = {f"{self.geo_col}__intersects": bbox}
        return query.filter(**intersect)

    def _build_mvt_query(self, x, y, z, filters):
        """
        Args:
            filters (dict): keys represent column names and values represent column
                            values to filter on.
        Returns:
            tuple:
            A tuple of length two.  The first element is a string representing a
            parameterized SQL query WHERE clause.  The second element is a list
            of parameters used as inputs to the WHERE clause.
        """
        query = self._get_mvt_geom_query(x, y, z)
        query = self._filter_query(query, x, y, z, filters)

        try:
            sql, params = query.query.sql_with_params()
        except FieldError as error:
            raise ValidationError(str(error))
        with connection.cursor() as cursor:
            return cursor.mogrify(sql, params).decode("utf-8")

    def _get_non_geom_columns(self):
        """
        Retrieves all table columns that are NOT the defined geometry column
        """
        columns = []
        for field in self.model._meta.get_fields():
            if hasattr(field, "get_attname_column"):
                column_name = field.get_attname_column()[1]
                if column_name != self.geo_col:
                    columns.append(column_name)
        return columns


class RegionMVTManager(MVTManager):
    def get_queryset(self):
        return (
            super(RegionMVTManager, self)
            .get_queryset()
            .annotate(bbox=models.functions.AsGeoJSON(models.functions.Envelope("geom")))
        )


class StaticMVTManager(MVTManager):
    def _filter_query(self, query, x, y, z, filters):
        query = super(StaticMVTManager, self)._filter_query(query, x, y, z, filters)
        region = REGION_ZOOMS[z]
        return query.filter(region__layer_type=region)


class LabelMVTManager(MVTManager):
    def get_queryset(self):
        return super(LabelMVTManager, self).get_queryset().annotate(geom_label=models.functions.Centroid("geom"))


class ClusterMVTManager(MVTManager):
    def get_queryset(self):
        return (
            super(ClusterMVTManager, self)
            .get_queryset()
            .annotate(center=models.functions.Centroid("geom"))
            .annotate(state_name=models.F("district__state__name"))
            .annotate(district_name=models.F("district__name"))
            .annotate(
                lat=X("center", output_field=models.DecimalField()), lon=Y("center", output_field=models.DecimalField())
            )
        )
