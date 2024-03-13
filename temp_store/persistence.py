from datetime import datetime
import os
from temp_store.domain import Location
from temp_store.store import DayStore, LocationStore 
from abc import abstractmethod

from psycopg2 import connect
from pymongo import MongoClient 



class TemperatureRepository:

    @abstractmethod
    def save(self, store: LocationStore) -> None:
        pass


    @abstractmethod
    def load(self, location: Location) -> LocationStore:
        pass


class LocationRepository:

    @abstractmethod
    def save(self, locations: dict[str, Location]) -> None:
        pass 

    @abstractmethod
    def load(self) -> dict[str, Location]:
        pass


        


class PostgresRepository(LocationRepository):

    def __init__(self) -> None:
        super().__init__()
        dbname = os.environ["POSTGRES_DB"]
        dbuser = os.environ["POSTGRES_USER"]
        dbpwd = os.environ["POSTGRES_PASSWORD"]
        dbserver = os.environ["POSTGRES_HOST"]
        self.connection = connect(f"dbname={dbname} user={dbuser} password={dbpwd} host={dbserver} port=5432")

    def load(self) -> dict[str, Location]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT location_name, latitude, longitude FROM locations")
        result : dict = {}
        for t in cursor.fetchall():
            result[t[0]] = Location(name=t[0], latitude=t[1], longitude=t[2])
        return result


    def save(self, locations: dict[str, Location]) -> None:
        cursor = self.connection.cursor()
        for l in locations.values():
            cursor.execute("""\
INSERT INTO locations (location_name, latitude, longitude) VALUES (%(n)s, %(lat)s, %(lon)s) 
ON CONFLICT ON CONSTRAINT locations_pkey DO UPDATE SET latitude=%(lat)s, longitude=%(lon)s""", {'n': l.name, 'lat': l.latitude, 'lon': l.longitude})
        self.connection.commit()


class MongoRepository(TemperatureRepository):

    def __init__(self) -> None:
        username = os.environ['MONGO_USER']
        password = os.environ['MONGO_PASSWORD']
        host = os.environ['MONGO_HOST']
        self.client : MongoClient = MongoClient(host=host, username=username, password=password)
        self.db = self.client.test_store

    def load(self, location: Location) -> LocationStore:
        coll = self.db[location.name]
        data = {}
        for bson in coll.find():
            keys = [datetime.fromisoformat(d) for d in bson.keys() if d != '_id']
            k = keys[0]
            day_store = DayStore(day=k.date(), location=location,temperatures={ ts : bson[ts.isoformat()] for ts in keys })
            data[k.date()] = day_store
        result = LocationStore(location=location, days=data)
        return result

    def save(self, store: LocationStore) -> None:
        coll = self.db[store.location.name] 
        for ds in store.days.values():
            coll.insert_one({ts.isoformat():v  for ts, v in ds.temperatures.items() })


