from __future__ import annotations
import math
from datetime import datetime
from pydantic.dataclasses import dataclass

# Earths radius
_R = 6371000


@dataclass(frozen=True)
class Location:
    name: str
    longitude: float
    latitude: float

    def __sub__(self, other: Location):
        """
        Distance between two GPS points in meters as per the haversine formula.

        Reading link:
        https://en.wikipedia.org/wiki/Haversine_formula
        """
        phi_1 = math.radians(self.latitude)
        phi_2 = math.radians(other.latitude)

        delta_phi = math.radians(other.latitude - self.latitude)
        delta_delta = math.radians(other.longitude - self.longitude)

        a =  math.sin(delta_phi / 2) * math.sin(delta_phi / 2) + math.cos(phi_1) * math.cos(phi_2) * (
            math.sin(delta_delta / 2) * math.sin(delta_delta / 2))

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
     
        d = _R * c

        return d

    def __repr__(self) -> str:
        return f"Location: {self.name} (lat={self.latitude}, lon={self.longitude})"

    def __str__(self) -> str:
        return f"POINT({self.longitude} {self.latitude})"


@dataclass(frozen=True)
class TemperatureRecording:
    location: Location
    timestamp: datetime
    value: float


