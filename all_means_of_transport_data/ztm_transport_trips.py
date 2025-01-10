import pandas as pd
from collections import defaultdict
from tqdm import tqdm

# Load data from the files
stop_times_file = "stop_times_ztm.txt"
stops_file = "stops_ztm.txt"

# Load data into DataFrames
stop_times = pd.read_csv(stop_times_file)
stops = pd.read_csv(stops_file)

# Create a dictionary to map stop_id to stop_name
stop_id_to_name = stops.set_index("stop_id")["stop_name"].to_dict()

# Dictionary to store the output structure
transport_data = defaultdict(lambda: defaultdict(list))

# Process each row in stop_times_ztm with progress bar
for _, row in tqdm(stop_times.iterrows(), total=len(stop_times), desc="Processing stop_times"):
    trip_id = row["trip_id"]
    stop_id = row["stop_id"]

    # Parse the trip_id to extract transport mode and route
    trip_parts = trip_id.split("_")
    if len(trip_parts) == 3:
        transport_mode = trip_parts[2].split("-")[0]  # Extract transport mode (e.g., 401)
        route = trip_parts[1]  # Extract route (e.g., 322)

        # Get the stop name from stop_id
        stop_name = stop_id_to_name.get(stop_id, "Unknown Stop")

        # Avoid duplicate routes for a transport mode
        if stop_name not in transport_data[transport_mode][route]:
            transport_data[transport_mode][route].append(stop_name)

# Generate the output
output_lines = []
for transport_mode, routes in tqdm(transport_data.items(), desc="Generating output"):
    output_lines.append(f"Transport mode {transport_mode}:")
    for route, stops in routes.items():
        output_lines.append(f"\tRoute {route}:")
        for stop in stops:
            output_lines.append(f"\t\t{stop}")

# Save the output to a text file
output_file = "transport_routes.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"Output has been saved to {output_file}")
