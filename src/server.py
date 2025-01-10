from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import threading
import json
import os
import sys
from find_nearest_stop import find_nearest_stop, load_stops
from integration_algorithm import *

PORT = 8000
stops = []
connections = {}

REACT_SCRIPT_PATH = "../app"
NPM_PATH = "..\\app\\node_modules\\.bin\\npm.cmd"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        # Obsługa POST requestu
        if self.path == "/run-script":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            script_name = data.get("script_name")
            print(data)

            if not script_name or not os.path.exists(script_name):
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Script not found"}).encode())
                return

            # Uruchamianie skryptu
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            stopData = data.get("startStop")
            run_algorithm(connections, stopData["id"], data["dateTime"].split('T')[1].split('.')[0])
            self.wfile.write(json.dumps("OK").encode())


        if self.path == "/get-nearest-stop":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            lat = data.get("lat")
            lng = data.get("lng")

            stop = find_nearest_stop(lat, lng, stops)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(stop).encode())

def run_interface():
    try:
        subprocess.run([NPM_PATH, "run", "dev"], cwd=REACT_SCRIPT_PATH, check=True, shell = True)
        print("React script started")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    except FileNotFoundError:
        print("Make sure npm is installed and added to your system PATH.")

if __name__ == "__main__":
    server = HTTPServer(('localhost', PORT), SimpleHTTPRequestHandler)
    stops = load_stops()
    connections = load_data()

    server_thread = threading.Thread(target = server.serve_forever)
    react_thread = threading.Thread(target = run_interface)

    server_thread.start()
    print(f"Server running on port {PORT}")
    react_thread.start()

    server_thread.join()
    react_thread.join()
    print("Closing server...")
