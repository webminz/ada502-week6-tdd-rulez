from datetime import datetime
from unittest import TestCase, main
from unittest.mock import MagicMock
from temp_store.domain import Location, TemperatureRecording

from temp_store.store import TemperatureRetriever, TemperatureStore

class Tests(TestCase):

    def test_store_and_retrieve(self):
        # 1. Set up
        store = TemperatureStore()
        lat, long = 60.36926,5.34975
        location = Location(longitude=long, latitude=lat)
        ts = datetime.fromisoformat("2024-01-31T12:00:00")
        store.store(location, ts, 5.2)
        # 2. calling the unit under test
        val = store.retrieve(location, datetime.fromisoformat("2024-01-31T12:00:00"))
        # 3. asserting
        expected = TemperatureRecording(location, datetime.fromisoformat("2024-01-31T12:00:00"), 5.2)
        self.assertEqual(expected, val)

    def test_retrieve_non_existing(self):
        store = TemperatureStore()
        lat, long = 60.36926,5.34975
        location = Location(longitude=long, latitude=lat)
        ts = datetime.fromisoformat("2024-01-31T12:31:55")
        val = store.retrieve(location, ts)
        self.assertIsNone(val)


    def test_web_retriever_into_store(self):
        retr = TemperatureRetriever()
        retr.retrieve = MagicMock(return_value=23)
        store = TemperatureStore()
        lat, long = 60.36926,5.34975
        location = Location(longitude=long, latitude=lat)
        ts = datetime(2024, 2, 1, 11, 0)
        data = retr.retrieve(location, ts)
        store.store(location, ts, data)
        val = store.retrieve(location, ts)

        retr.retrieve.assert_called_with(location, ts)
        expected = TemperatureRecording(location, ts, 23.0)

        self.assertEqual(expected, val)





if __name__ == "__main__":
    main()
