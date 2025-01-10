import json
import re

def normalize_station_name(name):
    return re.sub(r'\s?\d{2,3}\s?', '', name)

file_path = "routes.json"  

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

output_data = []

for route, journeys in data.items():
    route_info = {
        "route": route,
        "journeys": []
    }
    
    for journey in journeys:
        last_segment = journey["segments"][-1] 
        starting_stop = normalize_station_name(journey["segments"][0]["starting stop"]) 

        if "Miszewskiego" in starting_stop:
            journey_info = {
                "total_travel_time": journey["total travel time"],
                "starting_stop": starting_stop,
                "final_stop": normalize_station_name(last_segment["final stop"])  
            }
            route_info["journeys"].append(journey_info)
    
    if route_info["journeys"]:
        output_data.append(route_info)

output_file_path = "filtered_routes.json"

with open(output_file_path, "w", encoding="utf-8") as output_file:
    json.dump(output_data, output_file, ensure_ascii=False, indent=4)

print(f"Zapisano dane do pliku {output_file_path}")
