import requests
import json
from datetime import datetime

def fetch_otx_pulses(api_key, limit=10):
    headers = {
        'X-OTX-API-KEY': api_key
    }
    url = f'https://otx.alienvault.com/api/v1/pulses/subscribed?limit={limit}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        filename = f'otx_pulses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(f'data/{filename}', 'w') as f:
            json.dump(data, f, indent=2)
        return filename
    else:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")