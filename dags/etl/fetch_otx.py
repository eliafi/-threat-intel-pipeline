# etl/fetch_otx.py
import json
import os
from datetime import datetime
from OTXv2 import OTXv2, InvalidAPIKey

def fetch_otx_pulses(api_key, limit=5):
    try:
        otx = OTXv2(api_key)
        # Start with a smaller limit for faster execution
        pulses = otx.getall(limit=limit)  # Fetch subscribed pulses
    except InvalidAPIKey as e:
        raise ValueError("Invalid or missing OTX API key") from e

    # Create data directory if it doesn't exist
    data_dir = '/opt/airflow/data'
    os.makedirs(data_dir, exist_ok=True)
    
    filename = f'otx_pulses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(pulses, f, indent=2)
    return filename
