from OTXv2 import OTXv2
from OTXv2 import IndicatorTypes
import os

# Replace with your real API key
API_KEY = "c1744de2515fae01d69f476fe1c16cc12c361ccf2f84179095cad7c2702dc00e"

# Initialize client
otx = OTXv2(API_KEY)

# Example: Fetch latest pulses
def get_latest_pulses():
    pulses = otx.getall()
    for pulse in pulses[:5]:  # just print the first 5 for brevity
        print(f"Name: {pulse['name']}")
        print(f"Description: {pulse['description']}\n")

if __name__ == "__main__":
    get_latest_pulses()
