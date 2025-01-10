import json

# Funkcja sprawdzająca, czy dla każdego stop_id czasy travel_time do każdego innego stop_id są identyczne
def check_identical_travel_times_per_connection(connections):
    travel_times_identical = {}

    for stop_id, data in connections.items():
        travel_times_identical[stop_id] = {}

        # Sprawdzamy połączenia 'arrivals' (przyjazdy)
        for arrival in data['connections']['arrivals']:
            arrival_stop_id = arrival['stop_id']
            travel_times = [time['travel_time'] for time in arrival['times']]
            travel_time_set = set(travel_times)

            # Zapisujemy wynik dla danej pary stop_id
            travel_times_identical[stop_id][arrival_stop_id] = len(travel_time_set) == 1

        # Sprawdzamy połączenia 'departures' (odjazdy)
        for departure in data['connections']['departures']:
            departure_stop_id = departure['stop_id']
            travel_times = [time['travel_time'] for time in departure['times']]
            travel_time_set = set(travel_times)

            # Zapisujemy wynik dla danej pary stop_id
            travel_times_identical[stop_id][departure_stop_id] = len(travel_time_set) == 1

    return travel_times_identical

# Funkcja do zapisania wyników do pliku JSON
def save_to_json(connections, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(connections, f, ensure_ascii=False, indent=4)

# Główna część programu
if __name__ == "__main__":
    # 1. Wczytanie danych z pliku JSON
    with open('detailed_connections.json', 'r', encoding='utf-8') as f:
        detailed_connections = json.load(f)

    # 2. Sprawdzenie, czy dla każdego stop_id czasy travel_time do każdego innego stop_id są identyczne
    travel_times_identical = check_identical_travel_times_per_connection(detailed_connections)

    # 3. Zapisanie wyników sprawdzenia czasów przejazdu do pliku JSON
    identical_times_output_file = 'identical_travel_times.json'
    save_to_json(travel_times_identical, identical_times_output_file)

    print(f"Wyniki sprawdzenia czasów przejazdu zapisane do pliku {identical_times_output_file}")
