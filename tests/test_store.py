from unittest import TestCase, main
from unittest.mock import MagicMock

from temp_store.store import TemperatureRetriever, TemperatureStore

class Tests(TestCase):

    def test_store_and_retrieve(self):
        # 1. Set up
        store = TemperatureStore()
        lat, long = 60.36926,5.34975
        ts = "2024-01-31T12:31:55"
        store.store(lat, long, ts, 5.2)
        # 2. calling the unit under test
        val = store.retrieve(lat, long, ts)
        # 3. asserting
        self.assertEqual(5.2, val)

    def test_retrieve_non_existing(self):
        store = TemperatureStore()
        lat, long = 60.36926,5.34975
        ts = "2024-01-31T12:31:55"
        val = store.retrieve(lat, long, ts)
        self.assertIsNone(val)


    def test_web_retriever_into_store(self):
        retr = TemperatureRetriever()
        retr.retrieve = MagicMock(return_value=23)
        store = TemperatureStore()
        lat, long = 60.36926,5.34975
        ts = "2024-01-31T12:31:55"
        data = retr.retrieve(lat, long, ts)
        store.store(lat, long, ts, data)
        val = store.retrieve(lat, long, ts)
        retr.retrieve.assert_called_with( lat, long , ts)

        self.assertEqual(23, val)
        # ...





if __name__ == "__main__":
    main()
