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
        location = Location(name="hvl", longitude=long, latitude=lat)
        ts = datetime.fromisoformat("2024-01-31T12:31:13")
        store.store(location, ts, 5.2)
        # 2. calling the unit under test
        val = store.retrieve("hvl", datetime.fromisoformat("2024-01-31T12:31:13"))
        # 3. asserting
        expected = TemperatureRecording(location, datetime.fromisoformat("2024-01-31T12:31:13"), 5.2)
        self.assertEqual(expected, val)

    def test_retrieve_non_existing(self):
        store = TemperatureStore()
        lat, long = 60.36926,5.34975
        location = Location(name="hvl", longitude=long, latitude=lat)
        store.store(location, datetime.fromisoformat("2024-01-01T11:00:00"), 4)
        ts = datetime.fromisoformat("2024-01-31T12:31:55")
        val = store.retrieve("hvl", ts)
        self.assertIsNone(val)


    def test_web_retriever_into_store(self):
        retr = TemperatureRetriever()
        retr.retrieve = MagicMock(return_value=23)
        store = TemperatureStore()
        store.retriver = retr
        lat, long = 60.36926,5.34975
        location = Location(name="hvl", longitude=long, latitude=lat)
        ts = datetime(2024, 2, 1, 11, 0)
        data = retr.retrieve(location, ts)
        store.store(location, ts, data)
        val = store.retrieve("hvl", ts)

        retr.retrieve.assert_called_with(location, ts)
        expected = TemperatureRecording(location, ts, 23.0)

        self.assertEqual(expected, val)


if __name__ == "__main__":
    main()
