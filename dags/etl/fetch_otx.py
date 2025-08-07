# etl/fetch_otx.py
import json
from datetime import datetime
from OTXv2 import OTXv2, InvalidAPIKey

def fetch_otx_pulses(api_key, limit=10):
    try:
        otx = OTXv2(api_key)
        pulses = otx.getall(limit=limit)  # Fetch subscribed pulses
    except InvalidAPIKey as e:
        raise ValueError("Invalid or missing OTX API key") from e

    filename = f'otx_pulses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(f'data/{filename}', 'w') as f:
        json.dump(pulses, f, indent=2)
    return filename
