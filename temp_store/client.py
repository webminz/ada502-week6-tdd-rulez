import requests
from datetime import  datetime
from temp_store.domain import Location
from temp_store.store import TemperatureRetriever 


class MetClient(TemperatureRetriever):

    def __init__(self, client_id: str) -> None:
        super().__init__()
        self.client_id = client_id

    def retrieve(self, location: Location, from_ts: datetime, until_ts: datetime) -> list[float]:
        url = f"https://frost.met.no/sources/v0.jsonld?geometry=nearest({location})"
        r = requests.get(url, auth=(f'{self.client_id}',''))
        r.raise_for_status()

        d = r.json()
        sensor = d['data'][0]['id']

        obs_url = f"https://frost.met.no/observations/v0.jsonld?sources={sensor}&referencetime={from_ts.isoformat()}/{until_ts.isoformat()}&elements=air_temperature"

        r2 = requests.get(obs_url, auth=(f'{self.client_id}', ''))
        status = r2.status_code

        if status != 200:
            if status == 400:
                print(f"Invalid parameter value or malformed request: {obs_url}")
            if status == 401:
                print("Unauthorized client ID.")
            if status == 403:
                print(f"Too many observations requested. {obs_url}")
            if status == 404:
                print(f"No data was found for the query parameters: {obs_url}")
            if status == 412:
                print(f"No available time series for the query parameters: {obs_url}")
            if status == 429:
                print("The service is busy. Too many requests in progress. Retry-After is set with the number of seconds before the request should be retried again.")

            return []

        result = []
        for d in r2.json()['data']:
            for o in d['observations']:
                result.append(o['value'])
        return result


