import csv
import os
import sys
import json
from geopy.distance import geodesic

def load_stops():
    folders=['../app/public']    
    stops = []
    for folder in folders:
        filepath = os.path.join(folder, 'unified_stops.csv')  
        if os.path.exists(filepath):  
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)  
                    for row in reader:
                        stop_id = row[1]
                        stop_name = row[0]
                        stop_lat = float(row[2])
                        stop_lon = float(row[3])
                        stops.append({
                            'stop_id': stop_id,
                            'stop_name': stop_name,
                            'stop_lat': stop_lat,
                            'stop_lon': stop_lon
                        })
            except Exception as e:
                print(f'Błąd podczas wczytywania pliku {filepath}: {e}')
        else:
            print(f'Plik {filepath} nie istnieje w folderze {folder}.')
    return stops

def find_nearest_stop(user_lat, user_lon, stops):
    user_location = (user_lat, user_lon)
    nearest_stop = None
    min_distance = float('inf') 
    
    for stop in stops:
        stop_location = (stop['stop_lat'], stop['stop_lon'])
        distance = geodesic(user_location, stop_location).kilometers 
        if distance < min_distance:
            min_distance = distance
            nearest_stop = {
                "lat": stop_location[0],
                "lng": stop_location[1],
                "name": stop['stop_name'],
                "id": stop['stop_id']

            }
    return nearest_stop
