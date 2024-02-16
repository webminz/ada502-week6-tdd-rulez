from datetime import datetime
from unittest import TestCase, main
import os
from temp_store.client import MetClient


class IntegTest(TestCase):

    def test_frost_api(self):
        client_id = os.getenv('MET_CLIENT_ID')
        lat, long = 60.36930,5.35000
        ts = datetime(2024, 2, 8, 13, 1)
        client = MetClient()

        result = client.get_data(client_id, lat, long,  ts)
        self.assertTrue(isinstance(result, list))
        self.assertTrue(result[0], float)

if __name__ == "__main__":
    main()
