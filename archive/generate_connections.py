import pandas as pd
import json
from collections import defaultdict

# Funkcja do załadowania danych z plików GTFS
def load_gtfs_data():
    stops_df = pd.read_csv('ztm_gtfs_data/stops.txt')
    stop_times_df = pd.read_csv('ztm_gtfs_data/stop_times.txt')
    return stops_df, stop_times_df

# Funkcja do tworzenia połączeń z podziałem na przyjazdy i odjazdy (szczegółowe połączenia)
def create_detailed_connections(stops_df, stop_times_df):
    connections = defaultdict(lambda: {
        'stop_id': None,
        'stop_name': None,
        'lat': None,
        'lon': None,
        'connections': {
            'arrivals': defaultdict(lambda: {
                'stop_name': None,
                'times': []
            }),  # Stacje, z których przyjeżdżamy
            'departures': defaultdict(lambda: {
                'stop_name': None,
                'times': []
            })  # Stacje, do których odjeżdżamy
        }
    })

    # Przygotowujemy słownik z danymi o przystankach
    stops_info = {
        stop['stop_id']: {
            'stop_name': stop['stop_name'],
            'lat': stop['stop_lat'],
            'lon': stop['stop_lon']
        }
        for _, stop in stops_df.iterrows()
    }

    # Sortujemy stop_times, aby przetwarzać sekwencyjnie
    stop_times_df = stop_times_df.sort_values(by=['trip_id', 'stop_sequence'])

    # Poprzedni przystanek
    previous_stop = None
    previous_trip_id = None

    for index, stop_time in stop_times_df.iterrows():
        current_stop_id = stop_time['stop_id']
        trip_id = stop_time['trip_id']
        current_stop_sequence = stop_time['stop_sequence']
        arrival_time = stop_time['arrival_time']
        departure_time = stop_time['departure_time']

        # Zainicjalizowanie przystanku, jeśli jeszcze go nie mamy w connections
        if connections[current_stop_id]['stop_id'] is None:
            connections[current_stop_id]['stop_id'] = current_stop_id
            connections[current_stop_id]['stop_name'] = stops_info[current_stop_id]['stop_name']
            connections[current_stop_id]['lat'] = stops_info[current_stop_id]['lat']
            connections[current_stop_id]['lon'] = stops_info[current_stop_id]['lon']

        # Jeśli istnieje poprzedni przystanek i trip_id się zgadza, to budujemy połączenie
        if previous_stop and previous_trip_id == trip_id:
            previous_stop_id = previous_stop['stop_id']
            previous_departure_time = previous_stop['departure_time']

            # Dodajemy połączenia dwukierunkowe z odpowiednimi czasami
            travel_time = calculate_travel_time(previous_departure_time, arrival_time)

            # Dodanie połączenia jako przyjazd do bieżącego przystanku z poprzedniego
            connections[current_stop_id]['connections']['arrivals'][previous_stop_id]['stop_name'] = stops_info[previous_stop_id]['stop_name']
            connections[current_stop_id]['connections']['arrivals'][previous_stop_id]['times'].append({
                'arrival_time': arrival_time,
                'departure_time': previous_departure_time,
                'travel_time': travel_time
            })

            # Dodanie połączenia jako odjazd z poprzedniego przystanku do bieżącego
            connections[previous_stop_id]['connections']['departures'][current_stop_id]['stop_name'] = stops_info[current_stop_id]['stop_name']
            connections[previous_stop_id]['connections']['departures'][current_stop_id]['times'].append({
                'arrival_time': arrival_time,
                'departure_time': previous_departure_time,
                'travel_time': travel_time
            })

        # Zaktualizowanie informacji o poprzednim przystanku
        previous_stop = {
            'stop_id': current_stop_id,
            'departure_time': departure_time
        }
        previous_trip_id = trip_id  # Zapisanie bieżącego trip_id

    # Konwersja defaultdict na zwykły dict dla JSON
    connections = {k: dict(v) for k, v in connections.items()}
    for stop_id, data in connections.items():
        data['connections']['arrivals'] = [{
            'stop_id': str(arrival_stop_id),
            'stop_name': arrival_data['stop_name'],
            'times': arrival_data['times']
        } for arrival_stop_id, arrival_data in data['connections']['arrivals'].items()]

        data['connections']['departures'] = [{
            'stop_id': str(departure_stop_id),
            'stop_name': departure_data['stop_name'],
            'times': departure_data['times']
        } for departure_stop_id, departure_data in data['connections']['departures'].items()]

    return connections

# Funkcja do tworzenia uproszczonych połączeń (bez czasu przyjazdu i odjazdu)
def create_simplified_connections(detailed_connections):
    simplified_connections = {}

    for stop_id, data in detailed_connections.items():
        simplified_connections[stop_id] = {
            'stop_id': data['stop_id'],
            'stop_name': data['stop_name'],
            'lat': data['lat'],
            'lon': data['lon'],
            'connections': {
                'from': [],  # Z których przyjeżdżamy
                'to': []     # Do których odjeżdżamy
            }
        }

        # Dodajemy wszystkie unikalne stacje z 'arrivals' do 'from'
        for arrival in data['connections']['arrivals']:
            simplified_connections[stop_id]['connections']['from'].append({
                'stop_id': arrival['stop_id'],
                'stop_name': arrival['stop_name']
            })

        # Dodajemy wszystkie unikalne stacje z 'departures' do 'to'
        for departure in data['connections']['departures']:
            simplified_connections[stop_id]['connections']['to'].append({
                'stop_id': departure['stop_id'],
                'stop_name': departure['stop_name']
            })

    return simplified_connections

# Funkcja obliczająca czas przejazdu (w minutach) na podstawie arrival_time i departure_time
def calculate_travel_time(departure_time, arrival_time):
    dep_hours, dep_minutes, dep_seconds = map(int, departure_time.split(':'))
    arr_hours, arr_minutes, arr_seconds = map(int, arrival_time.split(':'))

    dep_total_minutes = dep_hours * 60 + dep_minutes + dep_seconds / 60
    arr_total_minutes = arr_hours * 60 + arr_minutes + arr_seconds / 60

    return round(arr_total_minutes - dep_total_minutes, 2)

# Funkcja do zapisania wyników do pliku JSON
def save_to_json(connections, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(connections, f, ensure_ascii=False, indent=4)

# Główna część programu
if __name__ == "__main__":
    # 1. Wczytanie danych z plików
    stops_df, stop_times_df = load_gtfs_data()

    # 2. Stworzenie połączeń z przyjazdami i odjazdami (szczegółowe)
    detailed_connections = create_detailed_connections(stops_df, stop_times_df)

    # 3. Zapisanie szczegółowych połączeń do pliku JSON
    detailed_output_file = 'detailed_connections.json'
    save_to_json(detailed_connections, detailed_output_file)

    # 4. Stworzenie uproszczonych połączeń (bez czasu przyjazdu i odjazdu)
    simplified_connections = create_simplified_connections(detailed_connections)

    # 5. Zapisanie uproszczonych połączeń do pliku JSON
    simplified_output_file = 'simplified_connections.json'
    save_to_json(simplified_connections, simplified_output_file)

    print(f"Szczegółowe połączenia zapisane do pliku {detailed_output_file}")
    print(f"Uproszczone połączenia zapisane do pliku {simplified_output_file}")
