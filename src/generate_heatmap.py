import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import matplotlib.colors as mcolors

def generate_heatmap(margin_size=0.02, gaussian_sigma=2, max_display_time=90):  # max_display_time w minutach
    # Zmienna kontrolująca wyświetlanie przystanków
    show_stops = True

    # Zmienna kontrolująca stopień transparentności
    transparency = 0.9  # Wartość od 0 (całkowicie przezroczysty) do 1 (całkowicie nieprzezroczysty)

    with open('travel_data.json', 'r', encoding='utf-8') as f:
        travel_data = json.load(f)

    # Odczyt współrzędnych i czasów podróży z nowej struktury JSON
    latitudes = [travel_data['start_station']['lat']] + [station['lat'] for station in travel_data['other_stations']]
    longitudes = [travel_data['start_station']['lon']] + [station['lon'] for station in travel_data['other_stations']]
    times = [travel_data['start_station']['travel_time']] + [station['travel_time'] for station in travel_data['other_stations']]

    # Upewnij się, że długości i szerokości są zgodne
    if len(latitudes) != len(longitudes) or len(latitudes) != len(times):
        raise ValueError("Liczba współrzędnych i czasów musi być zgodna.")

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

    # Generowanie siatki dla konturowania z użyciem marginesu
    grid_x, grid_y = np.mgrid[
                     (df['longitude'].min() - margin_size/2):(df['longitude'].max() + margin_size/2):100j,
                     (df['latitude'].min() - margin_size/2):(df['latitude'].max() + margin_size/2):100j
                     ]

    # Dodaj sztuczne punkty na krawędziach z dużymi wartościami czasu
    extra_points_x = np.array([min(df['x']) - margin_size, max(df['x']) + margin_size,
                               min(df['x']) - margin_size, max(df['x']) + margin_size])
    extra_points_y = np.array([min(df['y']) - margin_size, min(df['y']) - margin_size,
                               max(df['y']) + margin_size, max(df['y']) + margin_size])
    extra_points_time = np.array([max_time + 30, max_time + 30, max_time + 30, max_time + 30])

    # Dodaj sztuczne punkty do istniejących danych
    extended_x = np.concatenate((df['x'].values, extra_points_x))
    extended_y = np.concatenate((df['y'].values, extra_points_y))
    extended_times = np.concatenate((df['time'].values, extra_points_time))

    # Interpolacja liniowa na rozszerzonych danych
    grid_times = griddata((extended_x, extended_y), extended_times, (grid_x, grid_y), method='linear')

    # Maskowanie wartości powyżej maksymalnego czasu
    grid_times = np.where(grid_times > max_display_time, max_display_time, grid_times)

    # Rozciągnięcie ostatniej warstwy koloru na cały obszar tła
    grid_times = np.where(np.isnan(grid_times), max_display_time, grid_times)

    # Zastosowanie filtru Gaussa
    grid_times = gaussian_filter(grid_times, sigma=gaussian_sigma)

    # Ustawienia wykresu
    plt.figure(figsize=(10,8), dpi=100)
    ax = plt.gca()

    # Rysowanie konturowego heatmapu z poziomami co 2 minuty
    levels = np.linspace(0, max_display_time+10, 200)

    # Rysowanie konturowego heatmapu
    contour_plot = ax.contourf(grid_x, grid_y, grid_times, levels=levels, cmap='RdYlBu_r',  # Paleta kolorów
                               norm=mcolors.Normalize(vmin=0, vmax=max_display_time), alpha=transparency)

    if show_stops:
        # Rysowanie wszystkich przystanków jako czarne kropki
        ax.scatter(df['x'], df['y'], c='black', s=0.2, marker='o', label="Przystanki", linewidths=0)

        # Wyróżnienie przystanku początkowego jako większej, czerwonej kropki
        ax.scatter(df['x'].iloc[0], df['y'].iloc[0], c='red', s=2, marker='o', label="Przystanek początkowy")
        ax.legend()

    # Dodanie paska kolorów (colorbar)
    cbar = plt.colorbar(contour_plot, ax=ax, orientation='vertical', shrink=0.8, pad=0.02)
    cbar.set_label('Czas podróży (minuty)', fontsize=12)  # Opis skali
    cbar.ax.tick_params(labelsize=10)  # Rozmiar etykiet

    # Usunięcie osi
    ax.set_xticks([])
    ax.set_yticks([])

    # Zapis wykresu jako plik SVG
    plt.savefig('../app/public/heatmap.svg', format='svg', bbox_inches='tight', pad_inches=0)

if __name__ == "__main__":
    generate_heatmap(max_display_time=90)  # Przykładowo ustawiamy 90 minut
