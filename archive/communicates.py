import requests
import json

# URL to fetch data
url = "https://files.cloudgdansk.pl/d/otwarte-dane/ztm/bsk.json"

def fetch_data():
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to fetch data:", response.status_code)
        return None

# Fetch and display data
data = fetch_data()
if data:
    print(json.dumps(data, indent=2))  # Print the full JSON response
    for komunikat in data.get("komunikaty", []):
        print(f"Title: {komunikat['tytul']}")
        print(f"Content: {komunikat['tresc']}")
        print(f"Start: {komunikat['data_rozpoczecia']}")
        print(f"End: {komunikat['data_zakonczenia']}")
        print("-----------")
else:
    print("No data fetched")
