import pandas as pd

def load_stop_ids(file_path):
    """Wczytuje plik txt i zwraca listę unikalnych stop_id"""
    try:
        # Wczytanie pliku jako DataFrame
        df = pd.read_csv(file_path)
        
        # Zwraca kolumnę 'stop_id' jako listę
        return df['stop_id'].tolist()
    except Exception as e:
        print(f"Błąd podczas przetwarzania pliku {file_path}: {e}")
        return []

def find_common_stop_ids(file1, file2):
    """Znajduje wspólne stop_id między dwoma plikami txt"""
    # Wczytywanie stop_id z każdego plikuimport os
import pandas as pd
from collections import defaultdict

def load_stop_ids(file_path):
    """Wczytuje plik txt i zwraca listę unikalnych stop_id"""
    try:
        # Wczytanie pliku jako DataFrame
        df = pd.read_csv(file_path)
        
        # Zwraca kolumnę 'stop_id' jako lista
        return df['stop_id'].tolist()
    except Exception as e:
        print(f"Błąd podczas przetwarzania pliku {file_path}: {e}")
        return []

def find_common_stop_ids_in_folder(folder_path):
    """Znajduje wspólne stop_id między wszystkimi plikami w folderze"""
    # Lista plików w folderze zaczynających się od 'stops_' i kończących na '.txt'
    stop_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.startswith("stops_") and f.endswith(".txt")]
    
    # Słownik do przechowywania stop_id i listy plików, w których występują
    stop_id_to_files = defaultdict(list)
    
    # Przetwarzanie każdego pliku
    for stop_file in stop_files:
        stop_ids = load_stop_ids(stop_file)
        for stop_id in stop_ids:
            stop_id_to_files[stop_id].append(stop_file)
    
    # Znajdowanie wspólnych stop_id (tych, które występują w więcej niż jednym pliku)
    common_stop_ids = {stop_id: files for stop_id, files in stop_id_to_files.items() if len(files) > 1}
    
    # Wyświetlanie wyników
    if common_stop_ids:
        print("Przystanki o tych samych stop_id w różnych plikach:")
        for stop_id, files in common_stop_ids.items():
            print(f"Stop_id: {stop_id} występuje w plikach: {', '.join(files)}")
    else:
        print("Brak wspólnych przystanków o tych samych stop_id w plikach.")
        
# Przykład wywołania
folder_path = "stops_data"  # Ścieżka do folderu zawierającego pliki stops_*.txt
find_common_stop_ids_in_folder(folder_path)

    stop_ids1 = set(load_stop_ids(file1))
    stop_ids2 = set(load_stop_ids(file2))
    
    # Przecięcie zbiorów stop_id
    common_stop_ids = stop_ids1.intersection(stop_ids2)
    
    # Wyświetlanie wyników
    if common_stop_ids:
        print("Przystanki o tych samych stop_id w obu plikach:")
        for stop_id in common_stop_ids:
            print(f"Stop_id: {stop_id}")
    else:
        print("Brak wspolnych przystankow o tych samych stop_id w obu plikach.")

# Przykład wywołania
file1_path = 'stops_skm.txt'  # Ścieżka do pierwszego pliku txt
file2_path = 'stops_ztm.txt'  # Ścieżka do drugiego pliku txt

find_common_stop_ids(file1_path, file2_path)
