from datetime import datetime, timedelta
from unittest import TestCase, main
import os
from temp_store.client import MetClient
from temp_store.domain import Location


class IntegTest(TestCase):

    def test_frost_api(self):
        client_id = os.getenv('MET_CLIENT_ID')
        assert client_id is not None
        lat, long = 60.36930,5.35000
        location = Location(long, lat)
        ts = datetime(2024, 2, 8, 13, 1)
        until = ts + timedelta(hours=1)
        client = MetClient(client_id)
        result = client.retrieve(location,  ts, until)
        self.assertTrue(isinstance(result, list))
        self.assertTrue(result[0], float)

if __name__ == "__main__":
    main()
