import pandas as pd
import json
from collections import defaultdict
from tqdm import tqdm
import requests
import zipfile
import os
import logging

logging.basicConfig(level=logging.INFO)

# Dictionary of GTFS data sources
gtfs_sources = {
    "ztm": "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/30e783e4-2bec-4a7d-bb22-ee3e3b26ca96/download/gtfsgoogle.zip",
    "zkm": "http://api.zdiz.gdynia.pl/pt/gtfs.zip",
    "skm": "https://www.skm.pkp.pl/gtfs-mi-kpd.zip",
    "mzkw": "https://mkuran.pl/gtfs/wejherowo.zip"
}
def clear_folder(folder_path):
    if os.path.exists(folder_path):
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(folder_path)
        logging.info(f"Cleared existing folder: {folder_path}")

def download_and_extract_files(identifier, url):
    try:
        logging.info(f"Downloading GTFS data for {identifier} from {url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Temporary ZIP file name
        zip_filename = f"{identifier}_gtfs_data.zip"
        with open(zip_filename, 'wb') as f:
            f.write(response.content)
        logging.info(f"Downloaded {identifier} data: {zip_filename}")

        # Extract ZIP file
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            extract_folder = f"{identifier}_gtfs_data"
            os.makedirs(extract_folder, exist_ok=True)
            zip_ref.extractall(extract_folder)
            logging.info(f"Extracted {identifier} data to {extract_folder}")

            # Find and copy stops.txt to gtfs_data folder
            stops_file = os.path.join(extract_folder, "stops.txt")
            if os.path.exists(stops_file):
                new_stops_file = os.path.join(gtfs_data_folder, f"stops_{identifier}.txt")
                os.rename(stops_file, new_stops_file)
                logging.info(f"Saved stops.txt as {new_stops_file}")
            else:
                logging.warning(f"stops.txt not found for {identifier}")

            # Find and copy stoptimes.txt to gtfs_data folder
            stoptimes_file = os.path.join(extract_folder, "stop_times.txt")
            if os.path.exists(stoptimes_file):
                new_stoptimes_file = os.path.join(gtfs_data_folder, f"stoptimes_{identifier}.txt")
                os.rename(stoptimes_file, new_stoptimes_file)
                logging.info(f"Saved stop_times.txt as {new_stoptimes_file}")
            else:
                logging.warning(f"stop_times.txt not found for {identifier}")

        # Clean up temporary files
        os.remove(zip_filename)
        logging.info(f"Deleted zip file: {zip_filename}")

        # Optionally, remove the extracted folder
        for root, dirs, files in os.walk(extract_folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(extract_folder)
        logging.info(f"Deleted extracted folder: {extract_folder}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading data for {identifier}: {e}")
    except zipfile.BadZipFile as e:
        logging.error(f"Error extracting zip file for {identifier}: {e}")

def check_existing_files():
    if not os.path.exists(gtfs_data_folder):
        return False
    for identifier in gtfs_sources.keys():
        stops_file = os.path.join(gtfs_data_folder, f"stops_{identifier}.txt")
        stoptimes_file = os.path.join(gtfs_data_folder, f"stoptimes_{identifier}.txt")
        if not (os.path.exists(stops_file) and os.path.exists(stoptimes_file)):
            return False
    return True
# Function to load GTFS data from stops.txt and stop_times.txt
def load_gtfs_data(gtfs_directory):
    ztm_stops_df = pd.read_csv(f'{gtfs_directory}/stops_ztm.txt')
    ztm_stop_times_df = pd.read_csv(f'{gtfs_directory}/stoptimes_ztm.txt')
    zkm_stops_df = pd.read_csv(f'{gtfs_directory}/stops_zkm.txt')
    zkm_stop_times_df = pd.read_csv(f'{gtfs_directory}/stoptimes_zkm.txt')
    skm_stops_df = pd.read_csv(f'{gtfs_directory}/stops_skm.txt')
    skm_stop_times_df = pd.read_csv(f'{gtfs_directory}/stoptimes_skm.txt')
    mzkw_stops_df = pd.read_csv(f'{gtfs_directory}/stops_mzkw.txt')
    mzkw_stop_times_df = pd.read_csv(f'{gtfs_directory}/stoptimes_mzkw.txt')
    return ztm_stops_df, ztm_stop_times_df, zkm_stops_df, zkm_stop_times_df, skm_stops_df, skm_stop_times_df, mzkw_stops_df, mzkw_stop_times_df

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
def create_connections_by_trips_skm(stops_df, stop_times_df):
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
            stop_sequence = stop_time['stop_sequence']
            departure_time = fix_time_format(stop_time['departure_time'])

            # Initialize station data if not already done
            if connections[current_stop_id]['stop_id'] is None:
                connections[current_stop_id]['stop_id'] = int(current_stop_id)  # Cast to int
                connections[current_stop_id]['stop_name'] = stops_info[current_stop_id]['stop_name']
                connections[current_stop_id]['lat'] = float(stops_info[current_stop_id]['lat'])
                connections[current_stop_id]['lon'] = float(stops_info[current_stop_id]['lon'])

            # Check if the trip already exists for the current station
            if trip_id in connections[current_stop_id]['connections']:
                # Trip already exists, so only append the departure time if it's new
                if departure_time not in connections[current_stop_id]['connections'][trip_id]['departure_times']:
                    connections[current_stop_id]['connections'][trip_id]['departure_times'].append(departure_time)
                continue  # Skip adding stations again for this trip

            # Trip not yet defined for this station, so add departure times and to_stations
            connections[current_stop_id]['connections'][trip_id]['departure_times'].append(departure_time)

            # Get all stops for the current trip in stop_times, sorted by stop_sequence
            current_trip_stops = stop_times_df[stop_times_df['trip_id'] == trip_id].sort_values(by='stop_sequence')

            # Find where the current stop occurs in the trip by its stop_sequence
            current_stop_sequence = stop_time['stop_sequence']

            # Reset to_stations for this trip to ensure it only collects subsequent stations in this trip
            to_stations_for_this_trip = connections[current_stop_id]['connections'][trip_id]['to_stations']

            # Collect all stops after the current stop in this trip using stop_sequence
            for _, next_stop_time in current_trip_stops.iterrows():
                next_stop_sequence = next_stop_time['stop_sequence']

                # Only consider stops with a higher stop_sequence (i.e., later stops in the trip)
                if next_stop_sequence > current_stop_sequence:
                    next_stop_id = next_stop_time['stop_id']
                    next_trip_id = next_stop_time['trip_id']
                    next_arrival_time = fix_time_format(next_stop_time['arrival_time'])

                    # Ensure we are still in the same trip
                    if next_trip_id != trip_id:
                        print(f"Encountered a different trip at station {next_stop_id}, breaking loop.")
                        break  # Stop collecting if we encounter a different trip

                    # Calculate travel time between the departure time from the current stop and the arrival time at the next stop
                    travel_time = calculate_travel_time(departure_time, next_arrival_time)

                    # Add the next stop to the current stop's connections in the current trip
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

def save_to_json_skm(connections, output_file):
    # Convert defaultdict to a regular dict for JSON serialization
    filtered_connections = {}

    for stop_id, data in connections.items():
        # Filter out trips with empty 'to_stations'
        filtered_trips = {
            str(trip_id): trip_data  # Convert trip_id to str
            for trip_id, trip_data in data['connections'].items()
            if trip_data['to_stations']  # Keep only if 'to_stations' is not empty
        }

        # Only add stops that have at least one valid trip with connections
        if filtered_trips:
            filtered_connections[str(stop_id)] = {  # Convert stop_id to str
                'stop_id': data['stop_id'],
                'stop_name': data['stop_name'],
                'lat': data['lat'],
                'lon': data['lon'],
                'connections': filtered_trips
            }

    # Write the filtered connections data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_connections, f, ensure_ascii=False, indent=4)
def merge_json_files(input_files, output_file):
    merged_data = {}

    # Wczytywanie i łączenie zawartości każdego pliku JSON
    for file_path in input_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Dodawanie zawartości do głównego słownika
            merged_data.update(data)
    
    # Zapisanie połączonych danych do nowego pliku JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)


# Main part of the program
if __name__ == "__main__":
    gtfs_data_folder = "gtfs_data"
    ztm_output_file = 'ztm_connections_by_trips.json'
    zkm_output_file = 'zkm_connections_by_trips.json'
    skm_output_file = 'skm_connections_by_trips.json'
    mzkw_output_file = 'mzkw_connections_by_trips.json'
        # Check if data already exists and is complete
    if check_existing_files():
        logging.info("All required GTFS files already exist. Skipping download.")
    else:
        logging.info("GTFS data is incomplete or missing. Downloading...")
        if os.path.exists(gtfs_data_folder):
            clear_folder(gtfs_data_folder)
        os.makedirs(gtfs_data_folder, exist_ok=True)

        # Process each GTFS source
        for identifier, url in gtfs_sources.items():
            download_and_extract_files(identifier, url)

    # 1. Load data from GTFS sources
    ztm_stops_df, ztm_stop_times_df, zkm_stops_df, zkm_stop_times_df, skm_stops_df, skm_stop_times_df, mzkw_stops_df, mzkw_stop_times_df = load_gtfs_data(gtfs_data_folder)

    # Process ZTM
    if os.path.exists(ztm_output_file):
        logging.info("ZTM JSON file already exists. Skipping ZTM processing.")
    else:
        ztm_connections_by_trips = create_connections_by_trips(ztm_stops_df, ztm_stop_times_df)
        save_to_json(ztm_connections_by_trips, ztm_output_file)
        print(f"ZTM connections saved to {ztm_output_file}")

    # Process ZKM
    if os.path.exists(zkm_output_file):
        logging.info("ZKM JSON file already exists. Skipping ZKM processing.")
    else:
        zkm_connections_by_trips = create_connections_by_trips(zkm_stops_df, zkm_stop_times_df)
        save_to_json(zkm_connections_by_trips, zkm_output_file)
        print(f"ZKM connections saved to {zkm_output_file}")

    # Process SKM
    if os.path.exists(skm_output_file):
        logging.info("SKM JSON file already exists. Skipping SKM processing.")
    else:
        skm_connections_by_trips = create_connections_by_trips_skm(skm_stops_df, skm_stop_times_df)
        save_to_json_skm(skm_connections_by_trips, skm_output_file)
        print(f"SKM connections saved to {skm_output_file}")
        
        # Process SKM
    if os.path.exists(mzkw_output_file):
        logging.info("SKM JSON file already exists. Skipping SKM processing.")
    else:
        mzkw_connections_by_trips = create_connections_by_trips_skm(mzkw_stops_df, mzkw_stop_times_df)
        save_to_json_skm(mzkw_connections_by_trips, mzkw_output_file)
        print(f"SKM connections saved to {mzkw_output_file}")
        
    input_files_with = [ztm_output_file, zkm_output_file, skm_output_file, mzkw_output_file]
    output_file_with = 'merged_connections.json'
    input_files_without = [ztm_output_file, zkm_output_file,mzkw_output_file]
    output_file_without = 'merged_connections_without_skm.json'
    # Uruchomienie funkcji
    merge_json_files(input_files_with, output_file_with)
    print(f"Polaczony plik JSON zostal zapisany jako {output_file_with}")
    merge_json_files(input_files_without, output_file_without)
    print(f"Polaczony plik JSON zostal zapisany jako {output_file_without}")
