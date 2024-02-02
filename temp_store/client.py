import requests
import os 
from dotenv import load_dotenv
from datetime import datetime, timedelta

lat, long = 60.36915, 5.35021

url = f"https://frost.met.no/sources/v0.jsonld?geometry=nearest(POINT({long} {lat}))"

load_dotenv()
client_id = os.getenv('MET_CLIENT_ID')

r = requests.get(url, auth=(f'{client_id}',''))
r.raise_for_status()

d = r.json()

sensor = d['data'][0]['id']

from_ts = datetime(2024, 1, 31, 12, 30)
until_ts = from_ts + timedelta(hours=2)
from_ts = from_ts.isoformat().replace(' ', 'T')
until_ts = until_ts.isoformat().replace(' ', 'T')


obs_url = f"https://frost.met.no/observations/v0.jsonld?sources={sensor}&referencetime={from_ts}/{until_ts}&elements=air_temperature"

r2 = requests.get(obs_url, auth=(f'{client_id}', ''))
r2.raise_for_status()

d2 = r2.json()

for x in d2['data']:
    print(x['observations'][0]['value'])
