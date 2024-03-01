from abc import abstractmethod
from datetime import datetime
from temp_store.domain import Location, TemperatureRecording
import json

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

    def serialize(self) -> str:
        result = []
        for l in self.locations.keys():
            entry = {}
            entry['latitude'] = l.latitude
            entry['longitude'] = l.longitude
            m = self.locations[l]
            ll = []
            for ts in m.keys():
                ll.append({
                    'ts': ts.isoformat(),
                    'temperature': m[ts]
                })
            entry['temperatures'] = ll
            result.append(entry)
        return json.dumps(result)




    def retrieve(self, location: Location, ts: datetime) -> TemperatureRecording | None:
        if location in self.locations:
            location_map = self.locations[location]
            lookup_ts = datetime(year=ts.year, month=ts.month, day=ts.day, hour= ts.hour)
            if lookup_ts in location_map:
                value =  location_map[ts]
                return TemperatureRecording(location=location, timestamp=ts, value=value)
        return None
