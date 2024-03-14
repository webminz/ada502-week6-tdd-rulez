import logging
import os
from datetime import date, datetime


from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from fastapi.encoders import jsonable_encoder
from temp_store.client import MetClient
from temp_store.domain import Location 
from temp_store.persistence import MongoRepository, PostgresRepository
from temp_store.store import TemperatureStore

from dotenv import  load_dotenv






store = TemperatureStore()



def on_startup():
    load_dotenv()

    log_level = logging.INFO
    if "LOG_LEVEL" in os.environ:
        if os.environ["LOG_LEVEL"] == "DEBUG":
            log_level = logging.DEBUG
        elif os.environ["LOG_LEVEL"] == "WARN":
            log_level = logging.WARNING
        elif os.environ["LOG_LEVEL"] == "ERROR":
            log_level = logging.ERROR
    logging.basicConfig(filename="temp_store.log", encoding='utf-8', level=log_level)
    logging.info(f"Temperature Store Startup! Log Level: {logging.getLevelName(log_level)}")

    retriever = MetClient(os.environ['MET_CLIENT_ID'])
    store.retriver = retriever
    location_repo = PostgresRepository()
    temperature_repo = MongoRepository()

    store.locations = location_repo.load()
    for loc in store.locations.values():
        store._store[loc] = temperature_repo.load(loc)

    store.temperature_repo = temperature_repo
    store.location_repo = location_repo


# Serve static files


@asynccontextmanager
async def lifespan(app: FastAPI):
    on_startup()
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="pages"))

@app.get("/health") 
def healtcheck() -> Response:
    return Response()


@app.get("/{location}")
def get_temperature(location: str, timestamp: datetime) -> Response:
    result = store.retrieve(location, timestamp)
    if isinstance(result, str):
        logging.info(result)
        return PlainTextResponse(f"Location {location} does not exist", status_code=403)
    else:
        return JSONResponse(jsonable_encoder(result))

@app.post("/{location}")
def create_location(location: str, lat: float, lon: float) -> Response:
    result = store.create_location(location, lat, lon)
    if isinstance(result, str):
        return PlainTextResponse(result, status_code=400)
    else:
        return JSONResponse(jsonable_encoder(result))

        

@app.put("/{location}")
def collect_temperature(location: str, day: date) -> Response:
    loc = store.locations[location]
    if not loc:
        return PlainTextResponse(f"location {location} not found", status_code=404)
    logging.info(f"Updating data for location {location} on day {day}")
    if not store.retriver:
        logging.error("Retriever must not be None!")
        return PlainTextResponse(f"Retriever is not set", status_code=500)
    for ts, value in store.retriver.retrieve(loc, day).items():
        logging.debug(f"Got data for {ts}")
        store.store(loc, ts, value)
    return Response(status_code=201)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
 





