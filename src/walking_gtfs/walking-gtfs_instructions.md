# Testing Instructions for walking-gtfs.py

## Prerequisites
1. Python 3.x installed
2. Required Python packages:
   - requests
   - tqdm
   - logging (built-in)
   - json (built-in)
   - csv (built-in)
   - os (built-in)

## Setup Test Environment

1. Create a test directory and copy `walking-gtfs.py`  and `poi-map.py`   into it
2. Create a sample `poi.json` by using `poi-map.py`


## Test Cases

### 1. Basic Functionality Test
1. Run the script:
2. Verify that an `output_gtfs` directory is created
3. Check for the presence of four files:
   - stops_walking.txt
   - routes_walking.txt
   - trips_walking.txt
   - stop_times_walking.txt

### 2. File Content Verification
Check each output file for correct formatting:

#### stops_walking.txt:
- Should have 5 columns: stop_id, stop_name, stop_lat, stop_lon, stop_code
- Should contain 3 stops (one for each POI)
- Coordinates should match input POIs

#### routes_walking.txt:
- Should have 3 columns: route_id, route_name, route_type
- Should contain exactly one route with ID "1"

#### trips_walking.txt:
- Should have 3 columns: route_id, service_id, trip_id
- Should contain exactly one trip

#### stop_times_walking.txt:
- Should have 4 columns: stop_id, trip_id, stop_sequence, travel_time
- Should contain travel times between all POI pairs (6 entries for 3 POIs)
- Travel times should be positive integers (minutes)

### 3. API Response Test
1. Monitor the console output for any API errors
2. Verify that the OSRM API is responding (look for successful API calls in the logs)
3. Check if travel times are reasonable for walking distances

### 4. Error Handling Tests

#### Invalid JSON Test
1. Create a malformed poi.json file:
```json
[
    {
        "latitude": 40.7128,
        "longitude": -74.0060,
    } // Invalid JSON
]
```
2. Run the script and verify it logs an appropriate error

#### Network Error Test
1. Disconnect from the internet
2. Run the script
3. Verify it handles the network error gracefully

#### Empty Input Test
1. Create an empty poi.json file:
```json
[]
```
2. Run the script
3. Verify it handles empty input appropriately

## Success Criteria

The script is working correctly if:

1. All output files are generated with correct formatting
2. Travel times are reasonable for walking distances (check a few known distances)
3. No unhandled exceptions occur during normal operation
4. Error messages are clear and helpful
5. The progress bar shows accurate progress
6. Memory usage remains stable during execution

## Common Issues and Troubleshooting

1. If OSRM API is unresponsive:
   - Check internet connection
   - Verify OSRM_BASE_URL is accessible
   - Check if you're hitting rate limits

2. If travel times are missing:
   - Verify POI coordinates are valid
   - Check for API error responses in the logs
   - Verify timeout settings are appropriate

3. If performance is slow:
   - Check MAX_WORKERS setting
   - Monitor system resources
   - Verify network speed
