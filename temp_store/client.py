import requests
from datetime import  timedelta


class MetClient:

    def get_data(self, client_id, lat, long, ts):
        url = f"https://frost.met.no/sources/v0.jsonld?geometry=nearest(POINT({long} {lat}))"
        r = requests.get(url, auth=(f'{client_id}',''))
        r.raise_for_status()

        d = r.json()
        sensor = d['data'][0]['id']

        from_ts = ts
        until_ts = from_ts + timedelta(hours=2)
        from_ts = from_ts.isoformat().replace(' ', 'T')
        until_ts = until_ts.isoformat().replace(' ', 'T')

        obs_url = f"https://frost.met.no/observations/v0.jsonld?sources={sensor}&referencetime={from_ts}/{until_ts}&elements=air_temperature"

        r2 = requests.get(obs_url, auth=(f'{client_id}', ''))
        r2.raise_for_status()

        result = []
        for d in r2.json()['data']:
            for o in d['observations']:
                result.append(o['value'])
        return result


