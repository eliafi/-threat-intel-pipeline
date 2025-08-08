# Test script to verify OTX API key
from OTXv2 import OTXv2, InvalidAPIKey

def test_otx_connection(api_key):
    try:
        otx = OTXv2(api_key)
        # Try a simple call to get user info
        user_info = otx.get_user_info()
        print(f"✅ API Key is valid! User: {user_info.get('username', 'Unknown')}")
        return True
    except InvalidAPIKey as e:
        print(f"❌ Invalid API Key: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

# Test with your API key
if __name__ == "__main__":
    api_key = "YOUR_API_KEY_HERE"  # Replace with your actual key
    test_otx_connection(api_key)
