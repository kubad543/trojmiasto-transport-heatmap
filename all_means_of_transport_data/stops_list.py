import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

# Folder containing stops files
stops_data_folder = "gtfs_data"
output_csv_file = "../app/public/unified_stops.csv"

# Columns to extract from stops.txt
columns_to_extract = ["stop_name", "stop_id", "stop_lat", "stop_lon"]

# Initialize an empty DataFrame to store combined data
all_stops_data = pd.DataFrame()

# Process each stops_{identifier}.txt file
for stops_file in os.listdir(stops_data_folder):
    if stops_file.startswith("stops_") and stops_file.endswith(".txt"):
        identifier = stops_file.replace("stops_", "").replace(".txt", "")
        file_path = os.path.join(stops_data_folder, stops_file)

        try:
            # Read stops.txt
            stops_data = pd.read_csv(file_path)
            
            # Filter required columns
            stops_data_filtered = stops_data[columns_to_extract]
            
            # Add transport mode
            stops_data_filtered["transport_mode"] = identifier

            # Append to combined DataFrame
            all_stops_data = pd.concat([all_stops_data, stops_data_filtered], ignore_index=True)

        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")

# Reorder columns to desired order
all_stops_data = all_stops_data[["stop_name", "stop_id", "stop_lat", "stop_lon", "transport_mode"]]

# Sort alphabetically by stop_name
all_stops_data = all_stops_data.sort_values(by="stop_name", ignore_index=True)

# Save the sorted DataFrame to a CSV file
try:
    all_stops_data.to_csv(output_csv_file, index=False)
    logging.info(f"Combined and sorted stops data saved to {output_csv_file}")
except Exception as e:
    logging.error(f"Error saving to CSV: {e}")
