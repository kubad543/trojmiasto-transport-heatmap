import json
import re

def normalize_station_name(name):
    return re.sub(r'\s?\d{2,3}\s?', '', name.strip())

with open("filtered_routes.json", "r", encoding="utf-8") as file:
    data_from_google = json.load(file)

with open("travel_data.json", "r", encoding="utf-8") as file:
    data_from_algorithm = json.load(file)

final_stops = set()
for route in data_from_google:
    for journey in route["journeys"]:
        final_stop = normalize_station_name(journey["final_stop"])
        final_stops.add(final_stop)

matching_stations = []

for station in data_from_algorithm["other_stations"]:
    station_name = normalize_station_name(station["stop_name"])
    if station_name in final_stops:
        matching_stations.append({
            "stop_name": station_name,
            "travel_time_from_algorithm": station["travel_time"],  
            "travel_time_from_google": None  
        })

for route in data_from_google:
    for journey in route["journeys"]:
        final_stop = normalize_station_name(journey["final_stop"])  
        for matching_station in matching_stations:
            if matching_station["stop_name"] == final_stop:
                travel_time = re.sub(r"[^\d]", "", journey["total_travel_time"]) 
                matching_station["travel_time_from_google"] = travel_time

results = []
absolute_differences = []  

for station in matching_stations:
    if station["travel_time_from_google"] is not None:
        try:
            travel_time_from_algorithm = int(station["travel_time_from_algorithm"])  
            travel_time_from_google = int(station["travel_time_from_google"])  
            difference = abs(travel_time_from_algorithm - travel_time_from_google)
            absolute_differences.append(difference)  
            results.append({
                "stop_name": station["stop_name"],
                "travel_time_from_algorithm": travel_time_from_algorithm,
                "travel_time_from_google": travel_time_from_google,
                "time_difference": travel_time_from_algorithm - travel_time_from_google
            })
        except ValueError:
            results.append({
                "stop_name": station["stop_name"],
                "travel_time_from_algorithm": station["travel_time_from_algorithm"],
                "travel_time_from_google": station["travel_time_from_google"],
                "error": "Invalid travel time data"
            })
    else:
        results.append({
            "stop_name": station["stop_name"],
            "travel_time_from_algorithm": station["travel_time_from_algorithm"],
            "travel_time_from_google": None,
            "error": "No travel time data from the first file"
        })

if absolute_differences:
    mae = sum(absolute_differences) / len(absolute_differences)
else:
    mae = None

with open("results.json", "w", encoding="utf-8") as output_file:
    json.dump(results, output_file, ensure_ascii=False, indent=4)


print("Wyniki zapisano do pliku 'results.json'.")
if mae is not None:
    print(f"Średnia absolutna różnica (MAE): {mae:.2f} minut")
else:
    print("Nie można obliczyć MAE – brak wystarczających danych.")
