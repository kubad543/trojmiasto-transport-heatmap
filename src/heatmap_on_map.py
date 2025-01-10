import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import matplotlib.colors as mcolors
import folium
from folium.raster_layers import ImageOverlay

def generate_heatmap(margin_size=0.05, fixed_min_lat=None, fixed_min_lon=None, fixed_max_lat=None, fixed_max_lon=None):
    # Zmienna kontrolująca wyświetlanie przystanków
    show_stops = True

    # Zmienna kontrolująca stopień transparentności
    transparency = 0.6  # Wartość od 0 (całkowicie przezroczysty) do 1 (całkowicie nieprzezroczysty)

    with open('selected_stops.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Przygotowanie list dla współrzędnych i czasów
    latitudes = []
    longitudes = []
    times = []

    # Ekstrakcja szerokości, długości geograficznej i czasu podróży
    for stop_info in data.values():
        for connection_info in stop_info["connections"].values():
            for station_info in connection_info["to_stations"].values():
                latitudes.append(station_info["lat"])
                longitudes.append(station_info["lon"])
                times.append(station_info["time"])

    # Maksymalny czas do wyświetlenia na mapie
    max_time = max(times)

    # Tworzenie DataFrame
    df = pd.DataFrame({
        'latitude': latitudes,
        'longitude': longitudes,
        'time': times
    })

    # Używamy bezpośrednio współrzędnych WGS84 (EPSG:4326)
    df['x'] = df['longitude']
    df['y'] = df['latitude']

    # Ustalamy granice mapy na podstawie stałych szerokości i długości, jeśli zostały podane
    if fixed_min_lat is not None and fixed_min_lon is not None and fixed_max_lat is not None and fixed_max_lon is not None:
        min_lat = fixed_min_lat
        max_lat = fixed_max_lat
        min_lon = fixed_min_lon
        max_lon = fixed_max_lon
    else:
        # Jeśli nie ma stałych granic, dodajemy marginesy do dynamicznych granic przystanków
        min_lon = df['longitude'].min() - margin_size
        max_lon = df['longitude'].max() + margin_size
        min_lat = df['latitude'].min() - margin_size
        max_lat = df['latitude'].max() + margin_size

    # Generowanie siatki dla konturowania z użyciem marginesu
    grid_x, grid_y = np.mgrid[min_lon:max_lon:100j, min_lat:max_lat:100j]

    # Dodaj sztuczne punkty na krawędziach z dużymi wartościami czasu
    extra_points_x = np.array([min(df['x']) - margin_size, max(df['x']) + margin_size,
                               min(df['x']) - margin_size, max(df['x']) + margin_size])
    extra_points_y = np.array([min(df['y']) - margin_size, min(df['y']) - margin_size,
                               max(df['y']) + margin_size, max(df['y']) + margin_size])
    extra_points_time = np.array([max_time + 20, max_time + 20, max_time + 20, max_time + 20])

    # Dodaj sztuczne punkty do istniejących danych
    extended_x = np.concatenate((df['x'].values, extra_points_x))
    extended_y = np.concatenate((df['y'].values, extra_points_y))
    extended_times = np.concatenate((df['time'].values, extra_points_time))

    # Interpolacja liniowa na rozszerzonych danych
    grid_times = griddata((extended_x, extended_y), extended_times, (grid_x, grid_y), method='linear')

    # Ustawienia wykresu
    plt.figure(figsize=(10, 8), dpi=100)
    ax = plt.gca()

    # Rysowanie konturowego heatmapu z poziomami co 5 minut
    levels = np.arange(0, max_time + 10, 5)

    # Maskowanie wartości powyżej maksymalnego czasu
    grid_times = np.where(grid_times > max_time, max_time, grid_times)

    # Rozciągnięcie ostatniej warstwy koloru na cały obszar tła
    grid_times = np.where(np.isnan(grid_times), max_time, grid_times)

    # Rysowanie konturowego heatmapu
    ax.contourf(grid_x, grid_y, grid_times, levels=levels, cmap='RdYlBu_r',
                          norm=mcolors.Normalize(vmin=0, vmax=max_time), alpha=transparency)

    if show_stops:
        # Rysowanie wszystkich przystanków jako czarne kropki
        ax.scatter(df['x'], df['y'], c='black', s=1, marker='o', label="Przystanki")

        # Wyróżnienie przystanku początkowego jako większej, czerwonej kropki
        ax.scatter(df['x'].iloc[0], df['y'].iloc[0], c='red', s=10, marker='o', label="Przystanek początkowy")
        ax.legend()

    # Usunięcie osi
    ax.set_xticks([])
    ax.set_yticks([])

    # Zapis wykresu jako plik PNG
    plt.savefig('heatmap.png', bbox_inches='tight', pad_inches=0, dpi=600)

    return min_lat, min_lon, max_lat, max_lon

def overlay_heatmap_on_map(fixed_min_lat=-90, fixed_min_lon=-180, fixed_max_lat=90, fixed_max_lon=180):
    # Generowanie heatmapy z ustalonymi granicami
    generate_heatmap(
        fixed_min_lat=fixed_min_lat,
        fixed_min_lon=fixed_min_lon,
        fixed_max_lat=fixed_max_lat,
        fixed_max_lon=fixed_max_lon
    )

    # Define the boundaries of the overlay image based on fixed coordinates
    map_bounds = [
        [fixed_min_lat, fixed_min_lon],  # lower-left corner (south-west)
        [fixed_max_lat, fixed_max_lon]   # upper-right corner (north-east)
    ]

    # And the center of the map
    center_latitude = (fixed_min_lat + fixed_max_lat) / 2
    center_longitude = (fixed_min_lon + fixed_max_lon) / 2

    # Create a map object centered on your area of interest
    m = folium.Map(location=[center_latitude, center_longitude], zoom_start=13)

    # Overlay the heatmap image onto the map
    image_overlay = ImageOverlay(
        name='Heatmap Overlay',
        image='heatmap.png',
        bounds=map_bounds,
        opacity=0.6,
        interactive=True,
        cross_origin=False,
        zindex=1
    )

    # Add the overlay to the map
    image_overlay.add_to(m)

    # Add layer control so we can toggle the heatmap
    folium.LayerControl().add_to(m)

    # Save the map as an HTML file
    m.save('heatmap_map.html')

if __name__ == "__main__":
    overlay_heatmap_on_map(fixed_min_lat=54.2, fixed_min_lon=18.3, fixed_max_lat=54.6, fixed_max_lon=19.1)