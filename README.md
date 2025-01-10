# Heatmap - Trójmiasto  

## Overview  
**Heatmap - Trójmiasto** is an innovative application designed to visualize travel times across the Tricity area. The project aims to improve the understanding of urban transport efficiency by generating heatmaps that display travel accessibility for selected locations and times. The application combines real-time and static transportation data to provide a comprehensive and accurate view of the public transport network.  

The heatmap is generated dynamically within **5 seconds**, leveraging a custom routing algorithm to calculate travel times. This tool can be applied in urban planning to identify underserved areas in the transport network and optimize resource allocation.  

---

## Key Features  
- **Travel Time Heatmap**:  
  Generates a heatmap for the entire Tricity area, showing travel accessibility for a selected location and time.  
- **Real-Time Data Integration**:  
  Incorporates live data from ZTM (bus and tram schedules) and traffic services (Google/HERE).  
- **Static Data Support**:  
  Utilizes ZTM/ZKM (bus/tram) and SKM (train) schedules for route calculations.  
- **Custom Algorithm**:  
  Implements a breadth-first search algorithm to calculate shortest travel times for heatmap generation.  
- **Interactive Map Interface**:  
  Users can select a starting point, time, and mode of transport (bus, tram, train) through an intuitive UI.  
- **High Performance**:  
  Ensures graph creation and heatmap calculations are efficient, delivering results in under 10 seconds.  

---

## Applications  
- Identifying underutilized or poorly connected areas in the public transport network.  
- Supporting urban planning and decision-making by highlighting "dead zones" in transportation.  
- Analyzing and comparing the efficiency of different modes of transport in the Tricity area.  

---

## Tech Stack  
- **Backend**: Python  
- **Frontend**: React.js, Leaflet  
- **Data Sources**: ZTM APIs, SKM schedules, Google/HERE traffic data  
- **Infrastructure**: Google Cloud, Docker  

---

## My Contribution  
I was responsible for developing the **backend** of the application, which included:  
- Designing and implementing the custom routing algorithm using a graph-based approach.  
- Integrating static and real-time transportation data from ZTM, SKM, and traffic APIs.  
- Optimizing the backend to ensure heatmap generation within the 5-second performance benchmark.  
- Managing data processing and API interactions to support the frontend application.  

This project demonstrates strong backend development skills, including algorithm implementation, data integration, and performance optimization.
