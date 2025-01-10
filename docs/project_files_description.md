# HEATMAPA-TRÓJMIASTO

## OPIS APLIKACJI

**Stan na dzień 24.11.2024**

### BACKEND:

#### STRUKTURA DANYCH PRZYSTANKÓW I PODRÓŻY:
- `generate_connections_trips.py` (main/src/graph_generation)  
  Obsługa danych GTFS (rozkładów komunikacji publicznej), wykorzystywanie danych w postaci `stops.txt` i `stop_times.txt` do wygenerowania połączeń pomiędzy przystankami na podstawie tras. Tworzenie osobnej struktury dla danych Gdańsk i Gdynia oraz łączenie ich w jeden spójny plik JSON.
  
- `generate_data_stops.py` (main/src/graph_generation)  
  Generacja losowych danych o połączeniach z przystankami do wcześniejszych testów algorytmu przeszukiwania.
  
- `graph.py` (main/src/graph_generation)  
  Testowe GUI do sprawdzenia czasu i spójności wyszukiwania trasy na podstawie zawartości wygenerowanych plików JSON.

- `zkm_ztm_gtfs.py` (main/src/graph_generation)  
  Pobieranie plików GTFS z Gdańska i Gdyni oraz rozpakowanie ich do odpowiednich katalogów.

- `GTFS-RT.py` (GTFS-RT_data/src/graph_generation)  
  Przetwarzanie danych GTFS-RT w celu uwzględnienia opóźnień transportowych dla wyznaczonych połączeń w pliku JSON. Identyfikacja opóźnień dla kolejnych przystanków i tras oraz aktualizacja pliku JSON.

- `compare_stops.py` (creating_data_structures_for_other_means_of_transport/all_means_of_transport_data)  
  Porównanie plików `stops.txt`, czy nie ma powtarzających się identyfikatorów przystanków między różnymi środkami transportu.

- `generate_connections_trips_ztm.py` (creating_data_structures_for_other_means_of_transport/all_means_of_transport_data) 
  Przetwarzanie danych GTFS na temat transportu ZTM do wygenerowania połączeń między przystankami.

- `generate_connections_trips_skm.py` (creating_data_structures_for_other_means_of_transport/all_means_of_transport_data) 
  Przetwarzanie danych GTFS na temat transportu SKM do wygenerowania połączeń między przystankami. Ze względu na różnice w formacie danych SKM względem ZTM, kod odpowiedzialny za ich przetwarzanie jest osobny.

- `merge_jsons.py` (creating_data_structures_for_other_means_of_transport/all_means_of_transport_data)  
  Łączenie zawartości wielu plików JSON zawierających informacje o połączeniach przystanków różnych środków transportu w jeden plik.

#### Dodatkowe komponenty archiwalne:
- `communicates.py`  
  Pobieranie i wyświetlanie komunikatów związanych z opóźnieniami i awariami ZTM.

- `generate_connections.py`  
  Przetwarzanie danych ZTM do tworzenia uproszczonej i szczegółowej struktury połączeń między stacjami.

- `gtfs_stopdata.py`  
  Pobieranie i ekstrakcja odpowiednich danych ze zbioru ZTM.

- `schedule.py`  
  Działanie analogiczne do `gtfs_stopdata.py`. Wykorzystywany w `map.html`.

- `travel_times.py`  
  Analiza czasów między przystankami. Informacje przydatne w pierwszej wersji struktury JSON, gdzie przy połączeniu ze stacją wyświetlany był czas odjazdu, przyjazdu oraz podróży.

- `map.html`  
  Dynamiczna aplikacja mapowa wykorzystywana do testów obsługi danych.

- `proxy.js`  
  Serwer proxy umożliwiający dostęp do danych w czasie rzeczywistym.

- `style.css`  
  Stylizacja interfejsu `map.html`.

---

