import os
import json
import csv
import requests
import logging
from itertools import combinations
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import time
from requests.exceptions import RequestException

# Constants
OSRM_BASE_URL = "http://localhost:5000/route/v1/foot"
DEFAULT_TIMEOUT = 10  # seconds
MAX_WORKERS = 20  # Number of threads for parallel processing
BATCH_SIZE = 100  # Number of pairs per batch

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_travel_times_batch(poi_pairs, retries=3, delay=2):
    """
    Calculate walking travel times for multiple pairs of coordinates using batch requests.
    """
    results = []
    coordinates = ";".join([f"{lon1},{lat1};{lon2},{lat2}" for (lat1, lon1, lat2, lon2) in poi_pairs])
    url = f"{OSRM_BASE_URL}/{coordinates}"
    params = {"overview": "false", "geometries": "geojson"}

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if "routes" in data and len(data["routes"]) > 0:
                for route in data["routes"]:
                    duration = route.get("duration", None)
                    results.append(round(duration / 60) if duration else None)
                return results
            else:
                logging.warning("No routes found for batch.")
                return [None] * len(poi_pairs)
        except RequestException as e:
            logging.error(f"Error in batch request (attempt {attempt + 1}): {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return [None] * len(poi_pairs)
        except Exception as e:
            logging.error(f"Unexpected error in batch request: {e}")
            return [None] * len(poi_pairs)


def load_json(file_path):
    """
    Load JSON data from a file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        raise


def write_csv(file_path, rows, headers):
    """
    Write data to a CSV file.
    """
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)
        logging.info(f"Successfully wrote {file_path}")
    except IOError as e:
        logging.error(f"Error writing to CSV file {file_path}: {e}")


def calculate_travel_times_batch(poi_data):
    """
    Calculate travel times for all pairs of POIs using batch processing.
    """
    poi_pairs = [(poi1['latitude'], poi1['longitude'], poi2['latitude'], poi2['longitude'])
                 for poi1, poi2 in combinations(poi_data, 2)]
    all_results = []

    for i in tqdm(range(0, len(poi_pairs), BATCH_SIZE), desc="Batch processing pairs"):
        batch = poi_pairs[i:i + BATCH_SIZE]
        batch_results = get_travel_times_batch(batch)
        all_results.extend(batch_results)

    return poi_pairs, all_results


def generate_gtfs(poi_file, output_dir):
    """
    Generate GTFS-compatible data from a list of points of interest.
    """
    logging.info(f"Generating GTFS data from {poi_file}...")
    os.makedirs(output_dir, exist_ok=True)

    # Load input data
    poi_data = load_json(poi_file)

    # Initialize GTFS components
    stops = []
    stop_times = []
    routes = [["1", "Walking Route", "3"]]  # Route ID, name, type
    trips = [["1", "1", "1"]]  # Route ID, service ID, trip ID

    # Generate stops
    for idx, poi in enumerate(poi_data):
        stop_id = str(idx + 1)
        stops.append([stop_id, f"Point {idx + 1}", poi['latitude'], poi['longitude'], ""])

    # Calculate travel times in batch
    poi_pairs, travel_times = calculate_travel_times_batch(poi_data)

    # Populate stop_times with travel times
    sequence = 1
    for ((lat1, lon1, lat2, lon2), travel_time) in zip(poi_pairs, travel_times):
        if travel_time is not None:
            stop_id_1 = str(poi_data.index({'latitude': lat1, 'longitude': lon1}) + 1)
            stop_id_2 = str(poi_data.index({'latitude': lat2, 'longitude': lon2}) + 1)
            # Add travel times for both directions
            stop_times.append([stop_id_1, "1", sequence, travel_time])
            sequence += 1
            stop_times.append([stop_id_2, "1", sequence, travel_time])
            sequence += 1

    # Write output files
    write_csv(os.path.join(output_dir, "stops_walking.txt"), stops,
              ["stop_id", "stop_name", "stop_lat", "stop_lon", "stop_code"])
    write_csv(os.path.join(output_dir, "routes_walking.txt"), routes, ["route_id", "route_name", "route_type"])
    write_csv(os.path.join(output_dir, "trips_walking.txt"), trips, ["route_id", "service_id", "trip_id"])
    write_csv(os.path.join(output_dir, "stop_times_walking.txt"), stop_times,
              ["stop_id", "trip_id", "stop_sequence", "travel_time"])


# Example usage
if __name__ == "__main__":
    generate_gtfs("poi.json", "output_gtfs")
