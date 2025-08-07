from OTXv2 import OTXv2, IndicatorTypes

api_key = "c1744de2515fae01d69f476fe1c16cc12c361ccf2f84179095cad7c2702dc00e"
otx = OTXv2(api_key)

indicator = "1.1.1.1"
print(f"Querying OTX for indicator: {indicator}")

result = otx.get_indicator_details_full(IndicatorTypes.IPv4, indicator)

print("API call result:")
print(result)
