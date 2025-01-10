import subprocess
import os
from algorithm import *
import generate_heatmap

CONNCECTIONS_PATH = "merged_connections.json"

def run_algorithm(connections, start, time):
    # subprocess.run(["python", "algorithm.py"], check=True)
    print("starting..")
    starting_algorithm(connections, start, time)
    run_heatmap()

def run_heatmap():
    subprocess.run(["python", "generate_heatmap.py"], check=True)

def load_data():
    return load_connections(CONNCECTIONS_PATH)

if __name__ == "__main__":
    run_algorithm()
    run_heatmap()
