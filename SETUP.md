# Instructions for Running the Heatmap Project

This guide will walk you through the steps to run the Heatmap project and generate the connections for the trips.

## Requirements

Before you start, make sure you have the following software installed:

### 1. **Python 3.11**
- Python is required to run the scripts that generate transportation data. You can download it from [python.org](https://www.python.org/downloads/).
- The required Python libraries are listed in the `requirements.txt` file in the project directory. To install them, run:
  ```bash
  pip install -r requirements.txt

### 2. **Node.js (version 22.11.0 or higher)**
- Node.js and npm (Node package manager) are required to run the front-end part of the project.
- You can download Node.js from [nodejs.org](https://nodejs.org/en)
- After installation, check the versions by running the following commands:
  ```bash
  node -v
  npm -v
  ```

## Setup

### 1. Clone the Heatmap Project from GitHub
Clone the project repository to your local machine

### 2. Navigate to the `app` Directory
Open project and go to the `app` directory:
```bash
cd app
```
### 3. Install Project Dependencies
Install all the necessary project dependencies by running:
```bash
npm install npm --save-dev
```
It will install `npm.cmd` locally in project folder.

### 4. Download Connection Times for ZTM, ZKM, and PKM
Run the following Python script to download the connection times for ZTM, ZKM, and PKM, as well as their connections:
```bash
python ..\all_means_of_transport_data\generate_connections_trips_ztm_zkm_skm.py
```

### 5. Generate the Stops and Connections File
Now, run the Python script to generate the file with stops and connections:
```bash
python ..\all_means_of_transport_data\stops_list.py
```

This will create a file with the necessary data for generating the heatmap.

### 6. Run the Heatmap Application
Start the application by running (it runs server as well as react UI):
```bash
cd ..\src
python server.py
```
Server will run on `http://localhost:8000`.
The app will be available at `http://localhost:3000`.

### 7. Access the Application in Your Browser
Open your browser and go to:
http://localhost:3000

### 8. Choose the Starting Stop and Generate the Heatmap
Once you are on the Heatmap page, select the starting stop for your journey. It can be either clicked on the map or chosen from stops list, start time of your journey can be chosen as well. The heatmap will be generated based on the available data.

---
