import os
from datetime import date, datetime
from fastapi import FastAPI 

from fastapi.staticfiles import StaticFiles
from temp_store.client import MetClient

from temp_store.domain import Location, TemperatureRecording
from temp_store.store import TemperatureStore

from dotenv import  load_dotenv

load_dotenv()
app = FastAPI()
store = TemperatureStore()
retriever = MetClient(os.environ['MET_CLIENT_ID'])

# Serve static files
app.mount("/static", StaticFiles(directory="pages"))

@app.get("/")
def hello_word():
    return "Hei verden!"

@app.get("/greet/{name}")
def greet(name: str = "verden"):
    return f"Hei {name}!"


@app.get("/health") 
def get_user() -> bool:
    return True

@app.get("/{latitude}/{longitude}")
def get_temperature(latitude: float, longitude: float, timestamp: datetime) -> TemperatureRecording | None:
    return store.retrieve(Location(longitude, latitude), timestamp)

@app.post("/{latitude}/{longitude}")
def collect_temperature(latitude: float, longitude: float, date: date):
    location = Location(longitude, latitude)
    print(f"Updating data for location ({latitude}, {longitude}) from Frost API")
    for h in range(23):
        ts = datetime(date.year, date.month, date.day, h)
        ts_untl = datetime(date.year, date.month, date.day, h, 10)
        data = retriever.retrieve(location, ts, ts_untl)
        if len(data) > 0:
            print(f"Retrieved data for ({latitude}, {longitude}) {ts.isoformat()}")
            store.store(location, ts, data[0])






