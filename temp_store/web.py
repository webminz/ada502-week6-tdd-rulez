from typing import  Optional
from fastapi import FastAPI 
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles



class User(BaseModel):
    email : str 
    id : int


app = FastAPI()

app.mount("/static", StaticFiles(directory="pages"))

@app.get("/")
def hello_word():
    return "Hei!"

@app.get("/user") 
def get_user() -> User:
    return User(id=23, email="ole@nordmann.no")

@app.get("/weather")
def get_weather_bergen(location: Optional[str] = None) -> str:
    if location == "bergen":
        return "rainy"
    elif location == "oslo":
        return "snowy"
    else:
        return "dunno"






