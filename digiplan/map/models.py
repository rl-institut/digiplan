from dataclasses import dataclass
from enum import Enum

# from django.contrib.gis.db import models
# from django.utils.translation import gettext_lazy as _

# from .managers import RegionMVTManager, DistrictMVTManager, LabelMVTManager, MVTManager, ClusterMVTManager


class LayerFilterType(Enum):
    Range = 0
    Dropdown = 1


@dataclass
class LayerFilter:
    name: str
    type: LayerFilterType = LayerFilterType.Range
