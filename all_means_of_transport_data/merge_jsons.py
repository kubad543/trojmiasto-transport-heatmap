import json
import glob

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

# Specyfikacja plików wejściowych i pliku wyjściowego
input_files = glob.glob('connections_by_trips_*.json')  # Możesz dostosować wzorzec nazwy plików
output_file = 'merged_connections.json'

# Uruchomienie funkcji
merge_json_files(input_files, output_file)

print(f"Połączony plik JSON został zapisany jako {output_file}")
