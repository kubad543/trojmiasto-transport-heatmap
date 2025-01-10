
# Running OSRM Locally with Docker

This guide provides the steps to run the Open Source Routing Machine (OSRM) locally on your machine using Docker.

## Prerequisites
- **Docker**: Ensure you have Docker installed on your system. If not, follow the [official Docker installation guide](https://docs.docker.com/get-docker/).
- **OSRM Data File**: You will need a `.osm.pbf` file, which contains OpenStreetMap data. You can download by using a `download_pbf.py`

## Steps to Run OSRM Locally

### 1. Pull OSRM Docker Image
First, you need to pull the official OSRM backend Docker image.

```bash
docker pull osrm/osrm-backend
```

### 2. Prepare the Data
If you haven't already, download an OSM `.pbf` file by using download_pbf.py
```bash
python download_pbf.py 
```

Move the `.pbf` file to a directory on your system, e.g., `C:/osrm-data`.

### 3. Extract the Data
Use the following command to extract the data from the `.osm.pbf` file. This step prepares the map data for routing.

```bash
docker run -t -v C:/osrm-data:/data osrm/osrm-backend osrm-extract -p /opt/foot.lua /data/pomorskie-latest.osm.pbf
```

**Explanation**:

- The `-v C:/osrm-data:/data` option mounts the `C:/osrm-data` directory (adjust as needed) on your system to the `/data` directory inside the Docker container.

### 4. Build the Contracted Graph
After extracting the data, you need to build the contracted graph to optimize routing.

```bash
docker run -t -v C:/osrm-data:/data osrm/osrm-backend osrm-contract /data/pomorskie-latest.osrm
```

This step prepares the graph for quick routing.

### 5. Start the OSRM Server
Now that the graph is built, you can start the OSRM server to serve routing requests:

```bash
docker run -t -v C:/osrm-data:/data -p 5000:5000 osrm/osrm-backend osrm-routed /data/pomorskie-latest.osrm
```

**Explanation**:
- The `-p 5000:5000` option maps port 5000 on your local machine to port 5000 inside the Docker container.
- OSRM will now be accessible on `http://localhost:5000`.

### 6. Test the OSRM Server
Once the server is running, you can test it by sending an HTTP request to the API. For example:

```bash
python walking-gtfs.py  
```



### 7. Troubleshooting
- If you encounter errors like **"Could not find any metrics for MLD in the data"**, ensure that you have correctly extracted and contracted the data.
- If the server doesn't start or shows errors about missing files, ensure all steps (data extraction and contraction) have been completed successfully before starting the server.
#### 8. Effect (100 stops)
Calculating travel times: 100%|██████████| 4950/4950 [00:31<00:00, 156.79it/s]
2025-01-02 14:24:13,826 - INFO - Successfully wrote output_gtfs\stops_walking.txt
2025-01-02 14:24:13,827 - INFO - Successfully wrote output_gtfs\routes_walking.txt
2025-01-02 14:24:13,827 - INFO - Successfully wrote output_gtfs\trips_walking.txt
2025-01-02 14:24:13,830 - INFO - Successfully wrote output_gtfs\stop_times_walking.txt
#### 9. Problems
The server seems to throttle, and with a greater number of points, it slows down. It has phases of about 15-20 seconds where it runs very fast, but for about 80% of the time, it operates much slower.