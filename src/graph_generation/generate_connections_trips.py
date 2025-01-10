import pandas as pd
import json
from collections import defaultdict
from tqdm import tqdm

# Function to load GTFS data from stops.txt and stop_times.txt
def load_gtfs_data(gtfs_directory):
    stops_df = pd.read_csv(f'{gtfs_directory}/stops.txt')
    stop_times_df = pd.read_csv(f'{gtfs_directory}/stop_times.txt')
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

def extract_trip_number(trip_id):
    if isinstance(trip_id, str):
        return trip_id.split('_')[1]
    else:
        return str(trip_id)

# Function to create connections by trips
def create_connections_by_trips(stops_df, stop_times_df):
    connections = defaultdict(lambda: {
        'stop_id': None,
        'stop_name': None,
        'lat': None,
        'lon': None,
        'connections': defaultdict(lambda: {
            'departure_times': [],
            'to_stations': {}
        })
    })

    stops_info = {
        stop['stop_id']: {
            'stop_name': stop['stop_name'],
            'lat': stop['stop_lat'],
            'lon': stop['stop_lon']
        }
        for _, stop in stops_df.iterrows()
    }

    for current_stop_id in tqdm(stop_times_df['stop_id'].unique(), desc="Processing Stations"):
        stop_times_for_current_stop = stop_times_df[stop_times_df['stop_id'] == current_stop_id]

        for _, stop_time in stop_times_for_current_stop.iterrows():
            trip_id = stop_time['trip_id']
            trip_number = extract_trip_number(trip_id)
            stop_sequence = stop_time['stop_sequence']
            departure_time = fix_time_format(stop_time['departure_time'])

            if connections[current_stop_id]['stop_id'] is None:
                connections[current_stop_id]['stop_id'] = int(current_stop_id)
                connections[current_stop_id]['stop_name'] = stops_info[current_stop_id]['stop_name']
                connections[current_stop_id]['lat'] = float(stops_info[current_stop_id]['lat'])
                connections[current_stop_id]['lon'] = float(stops_info[current_stop_id]['lon'])

            if trip_number in connections[current_stop_id]['connections']:
                if departure_time not in connections[current_stop_id]['connections'][trip_number]['departure_times']:
                    connections[current_stop_id]['connections'][trip_number]['departure_times'].append(departure_time)
                continue

            connections[current_stop_id]['connections'][trip_number]['departure_times'].append(departure_time)

            current_trip_stops = stop_times_df[stop_times_df['trip_id'] == trip_id].sort_values(by='stop_sequence')
            current_stop_sequence = stop_time['stop_sequence']
            to_stations_for_this_trip = connections[current_stop_id]['connections'][trip_number]['to_stations']

            for _, next_stop_time in current_trip_stops.iterrows():
                next_stop_sequence = next_stop_time['stop_sequence']

                if next_stop_sequence > current_stop_sequence:
                    next_stop_id = next_stop_time['stop_id']
                    next_trip_id = next_stop_time['trip_id']
                    next_arrival_time = fix_time_format(next_stop_time['arrival_time'])

                    if extract_trip_number(next_trip_id) != trip_number:
                        break

                    travel_time = calculate_travel_time(departure_time, next_arrival_time)
                    to_stations_for_this_trip[str(next_stop_id)] = travel_time

    return connections

# Function to save connections to JSON file
def save_to_json(connections, output_file):
    connections = {str(k): dict(v) for k, v in connections.items()}
    for stop_id, data in connections.items():
        data['connections'] = {str(trip_id): {
            'departure_times': trip_data['departure_times'],
            'to_stations': {str(stop): time for stop, time in trip_data['to_stations'].items()}
        } for trip_id, trip_data in data['connections'].items()}

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(connections, f, ensure_ascii=False, indent=4)

# Main part of the program
if __name__ == "__main__":
    # 1. Load data from both GTFS sources
    ztm_stops_df, ztm_stop_times_df = load_gtfs_data('ztm_gtfs_data')
    gdynia_stops_df, gdynia_stop_times_df = load_gtfs_data('gdynia_gtfs_data')

    # 2. Create connections by trips for both sources
    ztm_connections_by_trips = create_connections_by_trips(ztm_stops_df, ztm_stop_times_df)
    gdynia_connections_by_trips = create_connections_by_trips(gdynia_stops_df, gdynia_stop_times_df)

    # 3. Save connections by trips to separate JSON files
    ztm_output_file = 'ztm_connections_by_trips.json'
    gdynia_output_file = 'gdynia_connections_by_trips.json'
    save_to_json(ztm_connections_by_trips, ztm_output_file)
    save_to_json(gdynia_connections_by_trips, gdynia_output_file)

    print(f"ZTM connections saved to {ztm_output_file}")
    print(f"Gdynia connections saved to {gdynia_output_file}")

    # 4. Load both JSON files
    with open(ztm_output_file, 'r', encoding='utf-8') as f:
        ztm_data = json.load(f)
    with open(gdynia_output_file, 'r', encoding='utf-8') as f:
        gdynia_data = json.load(f)

    # 5. Merge the two datasets
    merged_data = {**ztm_data, **gdynia_data}

    final_output_file = 'merged_connections_by_trips.json'
    with open(final_output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

    print(f"Final merged connections saved to {final_output_file}")
