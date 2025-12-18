import urllib.request
import urllib.parse
import json
import ssl

URL = "https://hr.parliament.gov.np/api/v1/members"
PARAMS = {
    "page": "1",
    "show_member": "active",
    "frontend_member_search": "true",
    "slug": "",
    "member_type": "member",
    "registered_date": "2074",
    "old_list": "true",
    "district_id": "",
    "political_party_id": "",
    "election_type_id": "",
    "gender": "",
    "all_member_listing": "true"
}

# Construct URL with params
query_string = urllib.parse.urlencode(PARAMS)
full_url = f"{URL}?{query_string}"

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_data():
    try:
        print(f"Fetching data from {full_url}...")
        req = urllib.request.Request(full_url, headers=HEADERS)
        
        # Ignore SSL errors if any (for development/testing)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.load(response)
            
            with open("parliament_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print("Data successfully saved to parliament_data.json")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_data()
