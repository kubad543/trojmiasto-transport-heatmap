import requests
import json
import pandas as pd
from google.transit import gtfs_realtime_pb2
from tqdm import tqdm


def fetch_gtfs_rt(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching GTFS-RT feed: {response.status_code}")
    return response.content


def parse_trip_updates(gtfs_rt_data):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(gtfs_rt_data)

    gtfs_rt_full_data = []
    for entity in feed.entity:
        if entity.HasField("trip_update"):
            trip_update = entity.trip_update
            trip_id = trip_update.trip.trip_id

            for stop_time_update in trip_update.stop_time_update:
                stop_id = stop_time_update.stop_id
                arrival_delay = (
                    stop_time_update.arrival.delay if stop_time_update.HasField("arrival") else 0
                )

                if arrival_delay >= 60 or arrival_delay <= -60:
                    gtfs_rt_full_data.append({
                        "trip_id": trip_id,
                        "stop_id": stop_id,
                        "arrival_delay_seconds": arrival_delay
                    })

    return gtfs_rt_full_data


def precompute_stop_times_lookup(stop_times_file):
    """
    Precomputes a lookup dictionary from the stop_times.txt file.
    :param stop_times_file: Path to the stop_times.txt file.
    :return: Precomputed lookup dictionary indexed by (trip_id, stop_sequence).
    """
    # Load the stop_times.txt into a DataFrame
    stop_times_df = pd.read_csv(stop_times_file)

    stop_times_df["trip_id"] = stop_times_df["trip_id"].astype(str)
    stop_times_df["stop_id"] = stop_times_df["stop_id"].astype(str)
    stop_times_df["stop_sequence"] = stop_times_df["stop_sequence"].astype(int)

    stop_times_lookup = stop_times_df.set_index(["trip_id", "stop_sequence"]).to_dict(orient="index")
    return stop_times_lookup


def find_previous_stop_with_delay(gtfs_rt_full_data, stop_times_lookup):
    processed_delays = []

    for record in tqdm(gtfs_rt_full_data, desc="Processing GTFS-RT Records"):
        trip_id = record["trip_id"]
        delayed_stop_id = record["stop_id"]
        delay_seconds = record["arrival_delay_seconds"]

        # Find the current stop_sequence using the lookup dictionary
        current_sequence = None
        for (t_id, seq), stop_data in stop_times_lookup.items():
            if t_id == trip_id and stop_data["stop_id"] == delayed_stop_id:
                current_sequence = seq
                break

        if current_sequence is not None:
            # Lookup the previous stop using the precomputed dictionary
            previous_stop_data = stop_times_lookup.get((trip_id, current_sequence - 1), None)

            if previous_stop_data:
                previous_stop_id = previous_stop_data["stop_id"]
                #print(f"Previous stop_id found: {previous_stop_id}")
                processed_delays.append({
                    "trip_id": trip_id,
                    "connection_id": trip_id.split("_")[1],
                    "previous_stop_id": previous_stop_data["stop_id"],
                    "delay_minutes": delay_seconds // 60,
                    "delayed_stop_id": delayed_stop_id
                })

    return processed_delays


def update_json_with_delays(original_json, processed_delays):
    print(processed_delays)
    for delay_info in processed_delays:
        previous_stop_id = str(delay_info["previous_stop_id"])
        connection_id = str(delay_info["connection_id"])
        delay_minutes = delay_info["delay_minutes"]
        delay_stop = str(delay_info["delayed_stop_id"])

        if previous_stop_id in original_json:
            connections = original_json[previous_stop_id].get("connections", {})
            if connection_id in connections:
                to_station = connections[connection_id].get("to_stations", {})
                if delay_stop in to_station:
                    to_station[delay_stop] += delay_minutes
                    print(
                        f"Updated connection_id {connection_id} at stop_id {previous_stop_id} with delay {delay_minutes} minutes on stop:{delay_stop}")
                if delay_stop not in to_station:
                    print(
                        f"Missing stop {delay_stop} in to_stations for connection_id {connection_id} at stop_id {previous_stop_id}")

    return original_json


def save_to_json(data, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {output_file}")


def main():
    url = "http://ckan2.multimediagdansk.pl/gtfs-rt?feed=tripUpdates"
    stop_times_file = "ztm_gtfs_data/stop_times.txt"
    merged_connections_file = "merged_connections_by_trips.json"

    try:
        gtfs_rt_data = fetch_gtfs_rt(url)
        full_gtfs_rt_data = parse_trip_updates(gtfs_rt_data)
        save_to_json(full_gtfs_rt_data, "full_gtfs_rt_data.json")

        stop_times_lookup = precompute_stop_times_lookup(stop_times_file)

        processed_delays = find_previous_stop_with_delay(full_gtfs_rt_data, stop_times_lookup)

        with open(merged_connections_file, "r", encoding="utf-8") as f:
            original_json = json.load(f)

        updated_json = update_json_with_delays(original_json, processed_delays)

        save_to_json(updated_json, "updated_connections_with_delays.json")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
