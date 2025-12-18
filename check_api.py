import urllib.request
import json
import ssl

URL = "http://localhost:8195/api/v1/entities/?entity_type=person&limit=1000"

def check_api():
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(URL, context=ctx) as response:
            print(f"Status: {response.status}")
            data = json.load(response)
            print(f"Data length: {len(data)}")
            if len(data) > 0:
                print("First item keys:", data[0].keys())
                print("First item metadata:", data[0].get("metadata"))
                print("First item meta_data:", data[0].get("meta_data"))
            else:
                print("Data is empty!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()
