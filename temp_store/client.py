import logging
import requests
from datetime import  date, datetime, timedelta
from temp_store.domain import Location
from temp_store.store import TemperatureRetriever 


class MetClient(TemperatureRetriever):

    def __init__(self, client_id: str) -> None:
        super().__init__()
        self.client_id = client_id

    def retrieve(self, location: Location, day: date) -> dict[datetime, float]:
        url = f"https://frost.met.no/sources/v0.jsonld?geometry=nearest({location})"
        r = requests.get(url, auth=(f'{self.client_id}',''))
        r.raise_for_status()

        d = r.json()
        sensor = d['data'][0]['id']

        from_ts = datetime(day.year, day.month, day.day)
        until_ts = from_ts + timedelta(days=1)
        from_tss = from_ts.strftime("%Y-%m-%d")
        until_tss = until_ts.strftime("%Y-%m-%d")

        obs_url = f"https://frost.met.no/observations/v0.jsonld?sources={sensor}&referencetime={from_tss}/{until_tss}&elements=air_temperature"

        logging.debug(f"Retrieving: {obs_url}")
        r2 = requests.get(obs_url, auth=(f'{self.client_id}', ''))
        status = r2.status_code

        if status != 200:
            if status == 400:
                logging.warning(f"Invalid parameter value or malformed request: {obs_url}")
            if status == 401:
                logging.warning("Unauthorized client ID.")
            if status == 403:
                logging.warning(f"Too many observations requested. {obs_url}")
            if status == 404:
                logging.warning(f"No data was found for the query parameters: {obs_url}")
            if status == 412:
                logging.warning(f"No available time series for the query parameters: {obs_url}")
            if status == 429:
                logging.warning("The service is busy. Too many requests in progress. Retry-After is set with the number of seconds before the request should be retried again.")

            return {}

        response_data = r2.json()
        logging.debug(f"Got {response_data['totalItemCount']} results")
        result : dict[datetime, float] = {}
        for d in response_data['data']:
            if d['referenceTime']:
                ts = datetime.fromisoformat(d['referenceTime'][:-1]) # get rid of the Z that confuses python
                for o in d['observations']:
                    if o['elementId'] == 'air_temperature' and o['value']:
                        result[ts] = o['value']
                        break
        return result


