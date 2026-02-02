
import requests

url = "https://www.bnm.md/en/official_exchange_rates?get_xml=1&date=02.02.2026"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print("Headers:")
    for key, value in response.headers.items():
        print(f"{key}: {value}")
except Exception as e:
    print(f"Error: {e}")
