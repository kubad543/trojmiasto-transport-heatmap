import os
import requests
import zipfile
import pandas as pd

# URL for the GTFS file
GTFS_URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/30e783e4-2bec-4a7d-bb22-ee3e3b26ca96/download/gtfsgoogle.zip"
GTFS_FOLDER = "gtfs_data"
GTFS_ZIP_PATH = "gtfs_data.zip"

# Function to download GTFS data
def download_gtfs_data():
    print("Downloading GTFS file...")
    response = requests.get(GTFS_URL)
    with open(GTFS_ZIP_PATH, 'wb') as f:
        f.write(response.content)
    print("Download complete.")

# Function to extract the ZIP file and delete it afterward
def extract_gtfs_data():
    print("Extracting GTFS file...")
    with zipfile.ZipFile(GTFS_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(GTFS_FOLDER)
    print("Extraction complete.")
    
    # Delete the ZIP file after extraction
    if os.path.exists(GTFS_ZIP_PATH):
        os.remove(GTFS_ZIP_PATH)
        print("Deleted ZIP file.")

# Function to load a GTFS file into a DataFrame
def load_gtfs_file(file_name):
    file_path = os.path.join(GTFS_FOLDER, file_name)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        print(f"File {file_name} not found.")
        return None

# Load the stops.txt file and select stop_lat, stop_lon columns
def get_stops_data():
    stops_df = load_gtfs_file('stops.txt')
    if stops_df is not None:
        return stops_df[['stop_name', 'stop_lat', 'stop_lon']]
    else:
        return None

# Function to upload each file to the server (dummy function, add your upload logic)
def upload_file_to_server(file_path):
    # Replace this print with actual upload code.
    print(f"Uploading {file_path} to the server.")

# Main script execution
if __name__ == "__main__":
    # Download and extract GTFS data
    download_gtfs_data()
    extract_gtfs_data()

    # Get stops data
    stops_data = get_stops_data()
    
    # Check data
    if stops_data is not None:
        print(stops_data.head())
        
        # Upload each GTFS file to the server
        for file_name in ['agency.txt', 'calendar_dates.txt', 'feed_info.txt', 'routes.txt', 
                          'shapes.txt', 'stop_times.txt', 'stops.txt', 'trips.txt']:
            upload_file_to_server(os.path.join(GTFS_FOLDER, file_name))

        # Optionally, delete the GTFS data folder after processing
        if os.path.exists(GTFS_FOLDER):
            for root, dirs, files in os.walk(GTFS_FOLDER, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(GTFS_FOLDER)
            print("Deleted GTFS data folder.")
    else:
        print("Failed to load stop data.")
