import requests

def download_pbf_file(region_name="pomorskie", output_file="pomorskie-latest.osm.pbf"):
    # Define the URL for the Geofabrik PBF file
    base_url = "https://download.geofabrik.de/europe/poland/"
    file_url = f"{base_url}{region_name}-latest.osm.pbf"

    try:
        print(f"Starting download from {file_url}...")

        # Send a GET request to the URL
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # Check for HTTP request errors

        # Save the file locally
        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Download complete! File saved as {output_file}.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    download_pbf_file()