from typing import List, Tuple
from datetime import datetime

from shapely.geometry import Polygon
from functools import cached_property

from dataclasses import dataclass


@dataclass
class Coordinate:
    lat: float
    lon: float


@dataclass
class Bounds:
    minlat: float
    minlon: float
    maxlat: float
    maxlon: float

    @property
    def bbox(self) -> list[float]:
        return [
            [self.minlat, self.minlon],  # bottom-left
            [self.minlat, self.maxlon],  # bottom-right
            [self.maxlat, self.maxlon],  # top-right
            [self.maxlat, self.minlon],  # top-left
            [self.minlat, self.minlon],  # close polygon
        ]


@dataclass
class BuildingInsight:
    building_id: int
    bounds: Bounds
    geometry: List[Coordinate]
    tags: dict

    @cached_property
    def centroid(self) -> Coordinate:
        centroid = Polygon([(c.lon, c.lat) for c in self.geometry]).centroid
        return Coordinate(lon=centroid.x, lat=centroid.y)
