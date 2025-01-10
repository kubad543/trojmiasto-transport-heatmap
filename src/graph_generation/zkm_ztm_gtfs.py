import requests
import zipfile
import os

# URL do pliku GTFS z Gdańska
url_ztm = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/30e783e4-2bec-4a7d-bb22-ee3e3b26ca96/download/gtfsgoogle.zip"
zip_filename_ztm = "ztm_gtfs_data.zip"

# Pobranie pliku GTFS z Gdańska
response_ztm = requests.get(url_ztm)
if response_ztm.status_code == 200:
    with open(zip_filename_ztm, 'wb') as f:
        f.write(response_ztm.content)
    print(f"GTFS file downloaded from ZTM Gdańsk: {zip_filename_ztm}")
else:
    print(f"Error while downloading data from ZTM Gdańsk: {response_ztm.status_code}")

# Rozpakowanie pliku GTFS z Gdańska
with zipfile.ZipFile(zip_filename_ztm, 'r') as zip_ref:
    zip_ref.extractall("ztm_gtfs_data")
    print(f"Unpacked ZTM Gdańsk file to folder: ztm_gtfs_data")

# Usunięcie pliku ZIP po rozpakowaniu
os.remove(zip_filename_ztm)
print(f"Deleted ZTM Gdańsk zip file: {zip_filename_ztm}")


# URL do pliku GTFS z Gdyni
url_gdynia = "http://api.zdiz.gdynia.pl/pt/gtfs.zip"
zip_filename_gdynia = "gdynia_gtfs_data.zip"

# Pobranie pliku GTFS z Gdyni
response_gdynia = requests.get(url_gdynia)
if response_gdynia.status_code == 200:
    with open(zip_filename_gdynia, 'wb') as f:
        f.write(response_gdynia.content)
    print(f"GTFS file downloaded from Gdynia: {zip_filename_gdynia}")
else:
    print(f"Error while downloading data from Gdynia: {response_gdynia.status_code}")

# Rozpakowanie pliku GTFS z Gdyni
with zipfile.ZipFile(zip_filename_gdynia, 'r') as zip_ref:
    zip_ref.extractall("gdynia_gtfs_data")
    print(f"Unpacked Gdynia file to folder: gdynia_gtfs_data")

# Usunięcie pliku ZIP po rozpakowaniu
os.remove(zip_filename_gdynia)
print(f"Deleted Gdynia zip file: {zip_filename_gdynia}")
