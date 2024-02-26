from abc import abstractmethod
from datetime import datetime
from temp_store.domain import Location, TemperatureRecording

class TemperatureRetriever:

    @abstractmethod
    def retrieve(self, location: Location, from_ts: datetime, until_ts: datetime) -> list[float]:
       pass 


class TemperatureStore:

    def __init__(self) -> None:
        self.locations : dict[Location, dict[datetime, float]] = {}

    def store(self, location: Location, ts: datetime, temp: float) -> None:
        """
        This method stores a temperature observation.
        """
        if location in self.locations:
            location_map = self.locations[location]
        else:
            location_map = {}
            self.locations[location] = location_map
        location_map[ts] = temp


    def retrieve(self, location: Location, ts: datetime) -> TemperatureRecording | None:
        if location in self.locations:
            location_map = self.locations[location]
            lookup_ts = datetime(year=ts.year, month=ts.month, day=ts.day, hour= ts.hour)
            if lookup_ts in location_map:
                value =  location_map[ts]
                return TemperatureRecording(location=location, timestamp=ts, value=value)
        return None
