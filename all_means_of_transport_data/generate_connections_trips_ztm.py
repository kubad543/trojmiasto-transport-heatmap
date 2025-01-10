import pandas as pd
import json
from collections import defaultdict
from tqdm import tqdm  # Import tqdm for progress bar

# Function to load GTFS data from stops.txt and stop_times.txt
def load_gtfs_data():
    stops_df = pd.read_csv('stops_ztm.txt')
    stop_times_df = pd.read_csv('stop_times_ztm.txt')
    return stops_df, stop_times_df

# Function to convert 24-hour format times like "25:02:00" to "01:02:00"
def fix_time_format(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    if hours >= 24:
        hours -= 24
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# Function to calculate travel time in minutes between departure and arrival
def calculate_travel_time(departure_time, arrival_time):
    dep_hours, dep_minutes, dep_seconds = map(int, departure_time.split(':'))
    arr_hours, arr_minutes, arr_seconds = map(int, arrival_time.split(':'))

    dep_total_minutes = dep_hours * 60 + dep_minutes + dep_seconds // 60
    arr_total_minutes = arr_hours * 60 + arr_minutes + arr_seconds // 60

    # Return the travel time in minutes
    return int(arr_total_minutes - dep_total_minutes)

# Function to extract the trip number (e.g., "101") from trip_id (e.g., "456202410060130_101_456-22")
def extract_trip_number(trip_id):
    return trip_id.split('_')[1]

# Function to create connections by trips
def create_connections_by_trips(stops_df, stop_times_df):
    connections = defaultdict(lambda: {
        'stop_id': None,
        'stop_name': None,
        'lat': None,
        'lon': None,
        'connections': defaultdict(lambda: {
            'departure_times': [],  # List of departure times from this station for the trip
            'to_stations': {}  # Dictionary of {stop_id: travel_time}
        })
    })

    # Prepare station information
    stops_info = {
        stop['stop_id']: {
            'stop_name': stop['stop_name'],
            'lat': stop['stop_lat'],
            'lon': stop['stop_lon']
        }
        for _, stop in stops_df.iterrows()
    }

    # Add tqdm to track the progress of processing each station
    for current_stop_id in tqdm(stop_times_df['stop_id'].unique(), desc="Processing Stations"):
        # Filter out all occurrences of the current stop in the stop_times dataframe
        stop_times_for_current_stop = stop_times_df[stop_times_df['stop_id'] == current_stop_id]

        # Iterate over each occurrence of the station in a trip
        for _, stop_time in stop_times_for_current_stop.iterrows():
            trip_id = stop_time['trip_id']
            trip_number = extract_trip_number(trip_id)
            stop_sequence = stop_time['stop_sequence']
            departure_time = fix_time_format(stop_time['departure_time'])

            # Initialize station data if not already done
            if connections[current_stop_id]['stop_id'] is None:
                connections[current_stop_id]['stop_id'] = int(current_stop_id)  # Cast to int
                connections[current_stop_id]['stop_name'] = stops_info[current_stop_id]['stop_name']
                connections[current_stop_id]['lat'] = float(stops_info[current_stop_id]['lat'])
                connections[current_stop_id]['lon'] = float(stops_info[current_stop_id]['lon'])

            # Check if the trip already exists for the current station
            if trip_number in connections[current_stop_id]['connections']:
                # Trip already exists, so only append the departure time if it's new
                if departure_time not in connections[current_stop_id]['connections'][trip_number]['departure_times']:
                    connections[current_stop_id]['connections'][trip_number]['departure_times'].append(departure_time)
                continue  # Skip adding stations again for this trip

            # Trip not yet defined for this station, so add departure times and to_stations
            connections[current_stop_id]['connections'][trip_number]['departure_times'].append(departure_time)

            # Get all stops for the current trip in stop_times, sorted by stop_sequence
            current_trip_stops = stop_times_df[stop_times_df['trip_id'] == trip_id].sort_values(by='stop_sequence')

            # Find where the current stop occurs in the trip by its stop_sequence
            current_stop_sequence = stop_time['stop_sequence']

            # Reset to_stations for this trip to ensure it only collects subsequent stations in this trip
            to_stations_for_this_trip = connections[current_stop_id]['connections'][trip_number]['to_stations']

            # Collect all stops after the current stop in this trip using stop_sequence
            for _, next_stop_time in current_trip_stops.iterrows():
                next_stop_sequence = next_stop_time['stop_sequence']

                # Only consider stops with a higher stop_sequence (i.e., later stops in the trip)
                if next_stop_sequence > current_stop_sequence:
                    next_stop_id = next_stop_time['stop_id']
                    next_trip_id = next_stop_time['trip_id']
                    next_arrival_time = fix_time_format(next_stop_time['arrival_time'])

                    # Ensure we are still in the same trip
                    if extract_trip_number(next_trip_id) != trip_number:
                        print(f"Encountered a different trip at station {next_stop_id}, breaking loop.")
                        break  # Stop collecting if we encounter a different trip

                    # Calculate travel time between the departure time from the current stop and the arrival time at the next stop
                    travel_time = calculate_travel_time(departure_time, next_arrival_time)

                    # Add the next stop to the current stop's connections in the current trip
                    to_stations_for_this_trip[str(next_stop_id)] = travel_time


    return connections

# Function to save connections to JSON file
def save_to_json(connections, output_file):
    # Convert defaultdict to a regular dict for JSON serialization
    connections = {str(k): dict(v) for k, v in connections.items()}
    for stop_id, data in connections.items():
        data['connections'] = {str(trip_id): {
            'departure_times': trip_data['departure_times'],
            'to_stations': {str(stop): time for stop, time in trip_data['to_stations'].items()}  # Use strings for stop_id
        } for trip_id, trip_data in data['connections'].items()}

    # Write the connections data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(connections, f, ensure_ascii=False, indent=4)

# Main part of the program
if __name__ == "__main__":
    # 1. Load data from stops.txt and stop_times.txt
    stops_df, stop_times_df = load_gtfs_data()

    # 2. Create connections by trips
    connections_by_trips = create_connections_by_trips(stops_df, stop_times_df)

    # 3. Save connections by trips to a JSON file
    output_file = 'connections_by_trips_ztm.json'
    save_to_json(connections_by_trips, output_file)

    print(f"Connections by trips saved to {output_file}")
