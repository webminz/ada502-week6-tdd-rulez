import logging
from abc import abstractmethod
from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict
from temp_store.domain import Location, TemperatureRecording



class TemperatureRetriever:

    @abstractmethod
    def retrieve(self, location: Location, day: date) -> dict[datetime, float]:
       pass 

class DayStore(BaseModel):
    location: Location
    day: date
    temperatures: dict[datetime, float]

    def get_closest(self, ts: datetime) -> float | None:
        if len(self.temperatures) == 0:
            return None 
        if ts in self.temperatures:
            return self.temperatures[ts]
        points = list(sorted(self.temperatures.keys()))
        left = points[0]
        right = points[1]
        for p in points:
            if p > ts:
                right = p 
                break
            else:
                left = p
        if ts - left > right - ts:
            return self.temperatures[left]
        else:
            return self.temperatures[right]

    def __add__(self, point: tuple[datetime, float]) -> None:
        self.temperatures[point[0]] = point[1]


class LocationStore(BaseModel):
    location: Location
    days: dict[date, DayStore]

    def __getitem__(self, day: date) ->  DayStore:
        if not day in self.days:
            self.days[day] = DayStore(location=self.location, day=day, temperatures={})
        return self.days[day]


class TemperatureRepository:

    @abstractmethod
    def add_measurement(self, location: str, ts: datetime, value: float) -> None:
        pass


    @abstractmethod
    def load(self, location: Location) -> LocationStore:
        pass


class LocationRepository:

    @abstractmethod
    def add_loaction(self, location: Location) -> None:
        pass 

    @abstractmethod
    def load(self) -> dict[str, Location]:
        pass


class TemperatureStore(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    locations: dict[str, Location] = {}
    _store: dict[Location, LocationStore] = {}

    retriver: TemperatureRetriever | None = Field(default=None, exclude=True)
    location_repo:  LocationRepository | None = Field(default=None, exclude=True)
    temperature_repo: TemperatureRepository | None = Field(default=None, exclude=True)
    

    def create_location(self, name: str, lat: float, lon: float) -> Location | str:
        if name in self.locations:
            return "location already exists"
        loc = Location(name=name, latitude=lat, longitude=lon)
        self.locations[name] = loc
        self._store[loc] = LocationStore(location=loc, days={})
        if self.location_repo:
            self.location_repo.add_loaction(loc)
        return loc


    def store(self, location: Location, ts: datetime, temp: float) -> None:
        """
        This method stores a temperature observation.
        """
        if not location in self._store:
            self.locations[location.name] = location
            self._store[location] = LocationStore(location=location, days={})
        day = ts.date()
        loc_store = self._store[location]
        loc_store[day] + (ts, temp)
        if self.temperature_repo:
            self.temperature_repo.add_measurement(location.name, ts, temp)


    def retrieve(self, location: str, ts: datetime) -> TemperatureRecording | str |None:
        if not location in self.locations:
            return f"location '{location}' is unknown!"
        day = ts.date()
        loc = self.locations[location]
        val = self._store[loc][day].get_closest(ts)

        if not val and self.retriver: 
            logging.info(f"Could not found data points at {loc} {ts} but retriever is registered. Will try to retrieve them now...")
            for point, temp in self.retriver.retrieve(loc, day).items():
                self.store(loc, point, temp)
            val = self._store[loc][day].get_closest(ts)
            
        if val:
            return TemperatureRecording(location=loc, timestamp=ts, value=val)
        return None
