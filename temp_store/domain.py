from datetime import datetime
from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class Location:
    longitude: float
    latitude: float

    def __str__(self) -> str:
        return f"POINT({self.longitude} {self.latitude})"

@dataclass(frozen=True)
class TemperatureRecording:
    location: Location
    timestamp: datetime
    value: float


