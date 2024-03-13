import logging
from datetime import date, datetime, timedelta
from unittest import TestCase, main
import os
from temp_store.client import MetClient
from temp_store.domain import Location
from temp_store.store import TemperatureStore


class IntegTest(TestCase):

    def test_frost_api(self):
        client_id = os.getenv('MET_CLIENT_ID')
        assert client_id is not None
        lat, long = 60.36930,5.35000
        location = Location("hvl", long, lat)
        client = MetClient(client_id)
        result = client.retrieve(location,date(2024, 2, 8))
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(result.values().__iter__().__next__(), float)

    def test_full(self):
        client_id = os.getenv('MET_CLIENT_ID')
        assert client_id is not None
        retriever = MetClient(client_id)
        store = TemperatureStore()
        store.retriver = retriever
        loc = store.create_location("hvl", 60.36930, 5.35000)
        ts = datetime(2024, 3, 11, 12 , 13)
        for ts, value in retriever.retrieve(loc, ts.date()).items():
            logging.info(f"Got {ts.isoformat()}: {value} -> storing")
            store.store(loc, ts, value)
        val = store.retrieve(loc.name, ts)
        self.assertIsNotNone(val)



if __name__ == "__main__":
    main()
