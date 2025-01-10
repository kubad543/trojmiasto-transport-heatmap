import json
import re
import matplotlib.pyplot as plt
import csv
from datetime import datetime, timedelta
from heapq import heappop, heappush

def load_connections(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    merged_connections = {}
    id_to_normalized_name = {}

    def normalize_stop_name(name):
        return re.sub(r"\s+\d+$", "", name)

    for stop_id, stop_data in data.items():
        normalized_name = normalize_stop_name(stop_data['stop_name'])
        id_to_normalized_name[stop_id] = normalized_name

        if normalized_name in merged_connections:
            existing_data = merged_connections[normalized_name]
            existing_data['latitudes'].append(stop_data['lat'])
            existing_data['longitudes'].append(stop_data['lon'])
            existing_data['stop_ids'].append(stop_id)

            for line_id, line_data in stop_data['connections'].items():
                if line_id not in existing_data['connections']:
                    existing_data['connections'][line_id] = {
                        "departure_times": line_data['departure_times'],
                        "to_stations": {}
                    }
                existing_line = existing_data['connections'][line_id]
                existing_line['departure_times'] = list(
                    set(existing_line['departure_times'] + line_data['departure_times']))
                for next_stop, travel_time in line_data['to_stations'].items():
                    normalized_next_stop = id_to_normalized_name.get(next_stop, next_stop)
                    if normalized_next_stop not in existing_line['to_stations']:
                        existing_line['to_stations'][normalized_next_stop] = travel_time

        else:
            merged_connections[normalized_name] = {
                "stop_name": normalized_name,
                "latitudes": [stop_data['lat']],
                "longitudes": [stop_data['lon']],
                "stop_ids": [stop_id],
                "connections": {}
            }
            for line_id, line_data in stop_data['connections'].items():
                new_line_data = {
                    "departure_times": line_data['departure_times'],
                    "to_stations": {}
                }
                for next_stop, travel_time in line_data['to_stations'].items():
                    normalized_next_stop = id_to_normalized_name.get(next_stop, next_stop)
                    new_line_data['to_stations'][normalized_next_stop] = travel_time
                merged_connections[normalized_name]['connections'][line_id] = new_line_data

    for stop_name, stop_data in merged_connections.items():
        for line_id, line_data in stop_data['connections'].items():
            line_data['to_stations'] = {id_to_normalized_name.get(stop, stop): time for stop, time in
                                        line_data['to_stations'].items()}

    return merged_connections

def generate_heatmap(start_location, start_time, connections):
    if start_location in connections:
        start_name = start_location
        start_id = start_location
    else:
        start_name = connections[start_location]['stop_name']
        start_id = start_location

    times = dijkstra_all_times(connections, start_id, start_time)

    lats, lons, travel_times = [], [], []

    start_stop_data = connections[start_name]
    for lat, lon in zip(start_stop_data["latitudes"], start_stop_data["longitudes"]):
        lats.append(lat)
        lons.append(lon)
        travel_times.append(0)

    for stop_id, travel_time in times.items():
        if stop_id != start_id and travel_time != float('inf'):
            stop_data = connections[stop_id]
            for lat, lon in zip(stop_data["latitudes"], stop_data["longitudes"]):
                lats.append(lat)
                lons.append(lon)
                travel_times.append(travel_time)

    with open('travel_times.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Latitude", "Longitude", "Travel Time (minutes)"])
        for lat, lon, travel_time in zip(lats, lons, travel_times):
            writer.writerow([lat, lon, travel_time])

    # NOT USED
    # plt.scatter(lons, lats, c=travel_times, cmap='hot', marker='o')
    # plt.colorbar(label='Travel time (minutes)')
    # plt.scatter(start_stop_data["longitudes"][0], start_stop_data["latitudes"][0], color='green', marker='o', s=100,
    #             label='Starting station')
    # plt.legend()
    # plt.title(f'Heatmap of travel times from {start_name} station')
    # plt.xlabel('Longitude')
    # plt.ylabel('Latitude')
    # plt.show()

    travel_data = {
        'start_station': {
            'lat': start_stop_data["latitudes"][0],
            'lon': start_stop_data["longitudes"][0],
            'travel_time': 0
        },
        'other_stations': [
            {'lat': lat, 'lon': lon, 'travel_time': time}
            for lat, lon, time in zip(lats[1:], lons[1:], travel_times[1:])
        ]
    }

    with open('travel_data.json', 'w', encoding='utf-8') as f:
        json.dump(travel_data, f, ensure_ascii=False, indent=4)

def starting_algorithm(connections, query, start_time):
    if isinstance(query, int) or (isinstance(query, str) and query.isdigit()):
        # Treat as stop_id
        stop_id = str(query)
        for stop_name, stop_data in connections.items():
            if stop_id in stop_data['stop_ids']:
                stop_name = str(stop_name)
                return {
                    generate_heatmap(stop_name, start_time, connections)
                }

    elif isinstance(query, list) and len(query) == 2 and all(isinstance(coord, (float, int)) for coord in query):
        # Treat as coordinates [latitude, longitude]
        latitude, longitude = query
        for stop_name, stop_data in connections.items():
            for lat, lon in zip(stop_data['latitudes'], stop_data['longitudes']):
                if abs(lat - latitude) < 1e-5 and abs(lon - longitude) < 1e-5:
                    stop_name = str(stop_name)
                    return {
                        generate_heatmap(stop_name, start_time, connections)
                    }

    elif isinstance(query, str):
        # Treat as stop name
        stop_name = query
        if stop_name in connections:
            stop_name = str(stop_name)
            return {
                generate_heatmap(stop_name, start_time, connections)
            }

def dijkstra_all_times(connections, start, departure_time):
    times = {stop_id: float('inf') for stop_id in connections}
    times[start] = 0

    visited = set()
    pq = [(0, start, departure_time)]

    while pq:
        current_time, current_stop, current_departure = heappop(pq)

        if current_stop in visited:
            continue

        visited.add(current_stop)

        for line_id, line_data in connections[current_stop]['connections'].items():
            for next_stop, travel_time in line_data['to_stations'].items():
                departure_times = sorted(line_data['departure_times'])

                scheduled_departure = None
                for dep_time in departure_times:
                    if dep_time >= current_departure:
                        scheduled_departure = dep_time
                        break

                if scheduled_departure is None:
                    continue

                scheduled_departure_dt = datetime.strptime(scheduled_departure, "%H:%M:%S")
                current_departure_dt = datetime.strptime(current_departure, "%H:%M:%S")
                wait_time = max((scheduled_departure_dt - current_departure_dt).seconds // 60, 0)

                total_travel_time = current_time + wait_time + travel_time

                if total_travel_time < 0:
                    total_travel_time += 1440

                if total_travel_time < times[next_stop]:
                    times[next_stop] = total_travel_time
                    heappush(pq,
                             (total_travel_time, next_stop, scheduled_departure))

    return times

if __name__ == "__main__":
    connections = load_connections('connections_by_trips.json')
    #testy
    starting_algorithm(connections, 1339, "08:00:00")

    starting_algorithm(connections, [54.355249766465, 18.596487931668], "08:00:00")

    starting_algorithm(connections, "Kurpińskiego", "08:00:00")

    starting_algorithm(connections, 1351, "20:00:00")

    starting_algorithm(connections, [54.367009035773, 18.612813161859], "20:00:00")

    starting_algorithm(connections, "Kręta", "20:00:00") 