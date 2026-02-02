
import urllib.request

url = "https://www.bnm.md/en/official_exchange_rates?get_xml=1&date=02.02.2026"

try:
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}")
        print("Headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
except Exception as e:
    print(f"Error: {e}")
