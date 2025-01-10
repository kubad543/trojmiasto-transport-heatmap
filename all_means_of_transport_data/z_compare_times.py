import json
import random

# Load the merged connections JSON file
def load_connections(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# Function to get the station name by its ID
def get_station_name_by_id(station_id, merged_connections):
    return merged_connections[str(station_id)]["stop_name"]

# Function to display connections with station names
def display_connections_with_names(merged_connections):
    # Choose a random station from the available keys (station IDs)
    random_station_id = random.choice(list(merged_connections.keys()))
    random_station_data = merged_connections[random_station_id]
    
    # Get the name of the selected station
    random_station_name = random_station_data["stop_name"]
    
    print(f"Station ID: {random_station_id}")
    print(f"Station Name: {random_station_name}\n")

    # Loop through the connections of the random station
    for line_id, line_data in random_station_data["connections"].items():
        print(f"Line ID: {line_id}")
        # For each 'to_station', get the name of the station and the time to reach it
        for to_station_id, travel_time in line_data["to_stations"].items():
            to_station_name = get_station_name_by_id(to_station_id, merged_connections)
            print(f"  - To: {to_station_name}, Travel Time: {travel_time} minutes")
        print("-" * 50)

# Main function to run the process
def main():
    # Load the merged connections data
    merged_connections = load_connections('merged_connections.json')
    
    # Display connections with station names
    display_connections_with_names(merged_connections)

if __name__ == "__main__":
    main()
