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
}

# Folder for storing extracted stops.txt files
stops_data_folder = "stops_data"
os.makedirs(stops_data_folder, exist_ok=True)

def download_and_extract_stops(identifier, url):
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

            # Find and copy stops.txt to stops_data folder
            stops_file = os.path.join(extract_folder, "stops.txt")
            if os.path.exists(stops_file):
                new_stops_file = os.path.join(stops_data_folder, f"stops_{identifier}.txt")
                os.rename(stops_file, new_stops_file)
                logging.info(f"Saved stops.txt as {new_stops_file}")
            else:
                logging.warning(f"stops.txt not found for {identifier}")

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

# Process each GTFS source
for identifier, url in gtfs_sources.items():
    download_and_extract_stops(identifier, url)