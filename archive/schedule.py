import requests
import zipfile
import os
import pandas as pd

# URL do pliku GTFS
url = 'https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/30e783e4-2bec-4a7d-bb22-ee3e3b26ca96/download/gtfsgoogle.zip'
zip_file = 'gtfsgoogle.zip'
extracted_folder = 'gtfs_data'

# Funkcja do pobrania pliku
def download_gtfs(url, zip_file):
    print("Downloading GTFS file...")
    response = requests.get(url)
    with open(zip_file, 'wb') as file:
        file.write(response.content)
    print("Download complete.")

# Funkcja do rozpakowania pliku
def unzip_file(zip_file, extract_to):
    print("Extracting GTFS...")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")

# Funkcja do wczytania pliku tekstowego do pandas DataFrame
def load_gtfs_file(file_name):
    file_path = os.path.join(extracted_folder, file_name)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        print(f"File {file_name} not found.")
        return None

# Pobranie i rozpakowanie danych
download_gtfs(url, zip_file)
unzip_file(zip_file, extracted_folder)

# Wczytanie plików GTFS do Pandas DataFrame
stops_df = load_gtfs_file('stops.txt')

# Zapisanie przystanków do pliku JSON
if stops_df is not None:
    stops_df.to_json('stops.json', orient='records')
    print("Saved stops data to stops.json")

# Usunięcie pliku ZIP po rozpakowaniu
if os.path.exists(zip_file):
    os.remove(zip_file)
    print("Deleted ZIP file.")

# Opcjonalnie, usunięcie rozpakowanego folderu po zapisaniu danych
if os.path.exists(extracted_folder):
    for root, dirs, files in os.walk(extracted_folder, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(extracted_folder)
    print("Deleted extracted data folder.")
