import json
import tkinter as tk
from tkinter import ttk
from collections import deque
from datetime import datetime, timedelta

# Load connections from JSON file
def load_connections(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# Function to calculate the travel time correctly considering midnight
def calculate_travel_time(start_time, travel_time):
    start_dt = datetime.strptime(start_time, "%H:%M:%S")
    travel_delta = timedelta(minutes=travel_time)
    end_dt = start_dt + travel_delta
    return end_dt.strftime("%H:%M:%S")

# BFS to find the shortest path considering waiting times
def bfs(connections, start, end, departure_time):
    queue = deque([(start, departure_time, [])])  # (current stop, departure time, path)
    visited = {start: departure_time}  # Store visited stops with their latest departure times

    while queue:
        current_stop, current_departure, path = queue.popleft()
        current_path = path + [(current_stop, current_departure)]  # Update the path

        if current_stop == end:
            return current_path  # Return the full path when the end is reached

        # Explore neighbors
        for next_trip, next_info in connections[current_stop]['connections'].items():
            for next_stop, travel_time in next_info['to_stations'].items():
                # Get the list of scheduled departure times
                departure_times = next_info['departure_times']

                # Find the next available departure time after the current time
                scheduled_departure = None
                for dep_time in departure_times:
                    if dep_time >= current_departure:
                        scheduled_departure = dep_time
                        break

                # If there's no valid scheduled departure time, continue to the next trip
                if scheduled_departure is None:
                    continue

                # Calculate the arrival time based on the scheduled departure time
                arrival_time = calculate_travel_time(scheduled_departure, travel_time)

                # Check if the arrival time is valid and the next stop has not been visited or has a later departure time
                if (arrival_time >= scheduled_departure and 
                    (next_stop not in visited or arrival_time < visited[next_stop])):
                    visited[next_stop] = arrival_time  # Record the arrival time at this stop
                    queue.append((next_stop, arrival_time, current_path))  # Add next stop to the queue

    return None  # Return None if no path is found

# Function to run the search when the button is pressed
def find_route():
    start_station = start_station_var.get()
    end_station = end_station_var.get()
    if not start_station or not end_station:
        result_label.config(text="Please select both start and end stations.")
        return

    # Update the current time before each route search
    current_time = datetime.now().strftime("%H:%M:%S")  # Current time as departure time

    start_id = station_id_map[start_station]
    end_id = station_id_map[end_station]

    route = bfs(connections, start_id, end_id, current_time)

    if route is None:
        result_label.config(text="No route found.")
    else:
        result_text = "Route:\n"
        total_travel_time = 0

        # Build the output string with travel times and arrival times
        for i in range(len(route) - 1):
            current_stop, departure_time = route[i]
            next_stop, _ = route[i + 1]

            # Fetch the travel time using the correct trip info
            travel_time = None
            for next_trip, next_info in connections[current_stop]['connections'].items():
                if next_stop in next_info['to_stations']:
                    travel_time = next_info['to_stations'][next_stop]
                    break

            if travel_time is not None:
                arrival_time = calculate_travel_time(departure_time, travel_time)

                result_text += f"{connections[current_stop]['stop_name']} -> {connections[next_stop]['stop_name']} " \
                               f"(Departure: {departure_time}, Travel Time: {travel_time} mins, Arrival: {arrival_time})\n"
                total_travel_time += travel_time

        result_text += f"\nTotal Travel Time: {total_travel_time} minutes"
        result_label.config(text=result_text)

# Load connections and prepare the GUI
if __name__ == "__main__":
    connections = load_connections('connections_by_trips.json')

    # Prepare station list and ID mapping sorted alphabetically
    station_id_map = {}
    stations = sorted(connections.keys(), key=lambda x: connections[x]['stop_name']) 
    for stop_id in stations:
        station_id_map[connections[stop_id]['stop_name']] = stop_id  

    # Initialize the Tkinter application
    root = tk.Tk()
    root.title("Transit Route Finder")

    # Create dropdowns for start and end stations
    start_station_var = tk.StringVar()
    end_station_var = tk.StringVar()

    ttk.Label(root, text="Select Start Station:").pack(pady=5)
    start_station_combobox = ttk.Combobox(root, textvariable=start_station_var, values=sorted(connections[stop_id]['stop_name'] for stop_id in connections))
    start_station_combobox.pack(pady=5)

    ttk.Label(root, text="Select End Station:").pack(pady=5)
    end_station_combobox = ttk.Combobox(root, textvariable=end_station_var, values=sorted(connections[stop_id]['stop_name'] for stop_id in connections))
    end_station_combobox.pack(pady=5)

    # Button to find route
    find_route_button = ttk.Button(root, text="Find Route", command=find_route)
    find_route_button.pack(pady=10)

    # Label to display results
    result_label = ttk.Label(root, text="")
    result_label.pack(pady=5)

    # Start the Tkinter main loop
    root.mainloop()
