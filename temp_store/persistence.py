from temp_store.store import TemperatureStore
from abc import abstractmethod

# Storage libraries
from minio import Minio
from psycopg2 import connect
from pymongo import MongoClient
from io import BytesIO

import json


class TemperatureStoreRepository:

    @abstractmethod
    def save(self, store: TemperatureStore) -> None:

        pass


    @abstractmethod
    def load(self) -> TemperatureStore:
        pass


        
class MinioRepository(TemperatureStoreRepository):

    def __init__(self, url: str, client_id: str, client_secret: str, ssl: bool = False) -> None:
        super().__init__()
        self.client = Minio(url, client_id, client_secret, secure=ssl)
        

    def save(self, store: TemperatureStore) -> None:
        json_str = store.serialize()
        json_bin = json_str.encode()
        buffer = BytesIO()
        byte_len = buffer.write(json_bin)
        self.client.put_object("temp_store_bucket", "store.json", buffer, byte_len)

    def load(self) -> TemperatureStore:
        return None # TODO implement
