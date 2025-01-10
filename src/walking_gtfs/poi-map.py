import json
import numpy as np

def generate_poi(num_points, sw_lat, sw_lng, ne_lat, ne_lng):
    # Oblicz liczbę punktów wzdłuż i wszerz
    num_per_dim = int(np.sqrt(num_points))
    
    lat_step = (ne_lat - sw_lat) / (num_per_dim - 1)
    lng_step = (ne_lng - sw_lng) / (num_per_dim - 1)
    
    points = []
    for i in range(num_per_dim):
        for j in range(num_per_dim):
            lat = sw_lat + i * lat_step
            lng = sw_lng + j * lng_step
            points.append({"latitude": lat, "longitude": lng})
    
    return points

def main():
    # Współrzędne Trójmiasta
    sw_lat = 54.31
    sw_lng = 18.45
    ne_lat = 54.63
    ne_lng = 18.90
    
    num_points = 1000
    
    poi = generate_poi(num_points, sw_lat, sw_lng, ne_lat, ne_lng)
    
    with open('poi.json', 'w') as file:
        json.dump(poi, file, indent=4)

if __name__ == '__main__':
    main()
