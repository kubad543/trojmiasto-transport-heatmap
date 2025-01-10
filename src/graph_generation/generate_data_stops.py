import random
import json
from datetime import datetime, timedelta

def generate_departure_times(num_times=10):
    """Generate random departure times in HH:MM:SS format."""
    times = []
    for _ in range(num_times):
        time = (datetime(2000, 1, 1) + timedelta(minutes=random.randint(0, 1440))).time()
        times.append(time.strftime('%H:%M:%S'))
    return times

def generate_connections(max_connections=8, max_times=10):
    """Generate a random number of connections with departure times and to_stations."""
    connections = {}
    num_connections = random.randint(1, max_connections)
    for connection_id in range(1, num_connections + 1):
        connections[str(connection_id)] = {
            "departure_times": generate_departure_times(random.randint(1, max_times)),
            "to_stations": {str(random.randint(1, 40)): random.randint(1, 30) for _ in range(random.randint(5, 15))}
        }
    return connections

def generate_stops(num_stops=40, max_connections=8, max_times=10):
    """Generate stops data for a specified number of stops."""
    stops = {}
    for stop_id in range(1, num_stops + 1):
        stops[str(stop_id)] = {
            "stop_id": stop_id,
            "stop_name": f"Stop {stop_id}",
            "lat": round(random.uniform(35.0, 55.0), 6),
            "lon": round(random.uniform(5.0, 19.0), 6),
            "connections": generate_connections(max_connections, max_times)
        }
    return stops

# Generate and save the dataset
stops_data = generate_stops(40)
with open("generated_stops.json", "w") as file:
    json.dump(stops_data, file, indent=4)

print("Data generated and saved to generated_stops.json")




def read_stops(file_path, num_stops=40):
    """Read stop information from stops.txt, select a limited number of stops, and skip the header line."""
    stops_data = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        next(file)  # Skip the header line
        for line in file:
            parts = line.strip().split(',')
            stop_id = int(parts[0])
            stop_name = parts[1]
            lat = float(parts[2])
            lon = float(parts[3])
            stops_data[stop_id] = {
                "stop_id": stop_id,
                "stop_name": stop_name,
                "lat": lat,
                "lon": lon
            }

    # Select a random subset of stops if there are more than num_stops
    selected_stops = dict(random.sample(stops_data.items(), num_stops))
    return selected_stops




def generate_connections2(available_stop_ids, max_connections=8, max_times=10):
    """Generate random connections with departure times and valid to_stations."""
    connections = {}
    num_connections = random.randint(1, max_connections)
    for connection_id in range(1, num_connections + 1):
        to_stations = {str(random.choice(available_stop_ids)): random.randint(1, 30)
                       for _ in range(random.randint(5, 15))}
        connections[str(connection_id)] = {
            "departure_times": generate_departure_times(random.randint(1, max_times)),
            "to_stations": to_stations
        }
    return connections


def generate_stops_with_data(stops_info, max_connections=8, max_times=10):
    """Generate stops data using given stop information with random connections."""
    stops = {}
    available_stop_ids = list(stops_info.keys())
    for stop_id, stop_data in stops_info.items():
        stops[str(stop_id)] = {
            **stop_data,
            "connections": generate_connections2(available_stop_ids, max_connections, max_times)
        }
    return stops


# Path to stops.txt and limit to 40 stops
stops_info = read_stops("stops.txt", num_stops=40)
stops_data = generate_stops_with_data(stops_info)

# Save the generated data to JSON
with open("generated_stops_with_actual.json", "w") as file:
    json.dump(stops_data, file, indent=4)

print("Data generated and saved to generated_stops2.json")

