import requests
import json

from datetime import datetime
import time


def get_transit_routes_details(api_key, origin, destinations, output_file="routes.json"):
    endpoint = "https://maps.googleapis.com/maps/api/directions/json"
    routes_data = {}  
    
    for destination in destinations:
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "transit",
            "alternatives": "true",
            "key": api_key
        }
        
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            data = response.json()
            routes = [] 
            
            if 'routes' in data:
                for route in data['routes']:
                    total_travel_time = 0  
                    route_segments = [] 
                    
                    for leg in route['legs']:
                        for step in leg['steps']:
                            if step['travel_mode'] == 'TRANSIT':
                                transit_details = step['transit_details']
                                line = transit_details['line']
                                departure_stop = transit_details['departure_stop']['name']
                                arrival_stop = transit_details['arrival_stop']['name']
                                line_name = line.get('short_name', line.get('name', 'N/A'))
                                duration = step['duration']['value'] // 60  
                                
                                departure_time = transit_details.get('departure_time', {}).get('text', 'Unknown')
                                
                                route_segments.append({
                                    "travel time": f"{duration} mins",
                                    "line number": line_name,
                                    "starting stop": departure_stop,
                                    "final stop": arrival_stop,
                                    "departure time": departure_time
                                })
                                
                                total_travel_time += duration
                    
                    if route_segments:
                        routes.append({
                            "total travel time": f"{total_travel_time} mins",
                            "segments": route_segments
                        })
            
            route_key = f"{origin} - {destination}"
            routes_data[route_key] = routes
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(routes_data, f, ensure_ascii=False, indent=4)
    
    print(f"Wyniki zapisano w pliku: {output_file}")


api_key = ""
origin = "Gdańsk, Miszewskiego"  
destinations = ["Gdańsk, Kołobrzeska", "Gdańsk, Jednorożca", "Gdańsk, Brodnicka", "Gdańsk, Nowatorów", "Gdynia, Starowiejska ", "Gdańsk, Oliwska ", "Gdańsk, Piwna", "Gdańsk, Sobieszewo", "Gdańsk, Barniewicka"] 

get_transit_routes_details(api_key, origin, destinations)