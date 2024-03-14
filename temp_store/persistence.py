import re
from datetime import datetime, date
import os
from temp_store.domain import Location
from temp_store.store import DayStore, LocationStore, LocationRepository, TemperatureRepository

from psycopg2 import connect
from pymongo import MongoClient 


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


    def add_loaction(self, location: Location) -> None:
        cursor = self.connection.cursor()
        cursor.execute("""\
INSERT INTO locations (location_name, latitude, longitude) VALUES (%(n)s, %(lat)s, %(lon)s)\
""", {'n': location.name, 'lat': location.latitude, 'lon': location.longitude})
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
            k = date.fromisoformat(bson['day'])
            day_store = DayStore(
                day=k,
                location=location,
                temperatures={ datetime.fromisoformat(ts) : val for ts, val in bson.items() if re.match(ts, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}") }
            )
            data[k] = day_store
        result = LocationStore(location=location, days=data)
        return result


    def add_measurement(self, location: str, ts: datetime, value: float) -> None:
        coll = self.db[location] 
        o = coll.find_one({'day': ts.date().isoformat()})
        if o:
            o[ts.isoformat()] = value
        else:
            o = {}
            o['day'] = ts.date().isoformat()
            o[ts.isoformat()] = value
            coll.insert_one(o)



