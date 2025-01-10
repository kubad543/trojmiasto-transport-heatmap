// components/SearchDropDown.js

"use client";
import React, { useState, useEffect } from 'react';
import DatetimeComponent from "./Datetime"; 
import styles from './styles/search.module.css'
import stylesButton from './styles/button.module.css'
import dayjs from 'dayjs';

const DropdownButton = ({selectedStartStop, setSelectedStartStop, setHeatmapUrl}) => {
  const [stopNames, setStopNames] = useState([]);
  const [activeDropdown, setActiveDropdown] = useState(null);
  // const [selectedEndStop, setSelectedEndStop] = useState(null);
  const [selectedDateTime, setSelectedDateTime] = useState(dayjs());

  useEffect(() => { 
    const fetchStops = async () => { 
      try { 
        const response = await fetch('/unified_stops.csv'); 
        const csvText = await response.text();
        const stops = csvText.split('\n').slice(1).map(line => {
        const [name, code, lat, lon, type] = line.split(',');
        return { name, code, lat, lon, type };
      });

    const stopNames = stops
    .filter(stop => stop.name && stop.type)
    .map(stop => ({ id: stop.code, name: stop.name, type: stop.type, lat: parseFloat(stop.lat), lon: parseFloat(stop.lon)}));
    console.log('Parsed stop names:', stopNames); setStopNames(stopNames); } 
  catch (error) { 
    console.error('Error fetching stops:', error); 
  } 
}; 
  fetchStops(); }, []);

  const handleSelectStop = (id, stop, lat, lon, type) => {
     if (type === 'start') { 
      const stopDetails = {id: id, name: stop, lat: lat, lon: lon};
      setSelectedStartStop(stopDetails);
    } 
    //  else if (type === 'end') { setSelectedEndStop(stop); } 
     setActiveDropdown(null); 
  };

  const handleSearch = async () => {
    console.log(selectedStartStop)
    try { 
      const response = await fetch('http://localhost:8000/run-script', {
        method: 'POST', 
        headers: { 
          'Content-Type': 'application/json'
        }, 
        body: JSON.stringify({ 
          script_name: "algorithm.py",
          startStop: selectedStartStop, 
          dateTime: selectedDateTime.toISOString()
        }),
        mode: 'no-cors' 
      });

      const _ = await response.text();
      setHeatmapUrl(`/heatmap.svg?timestamp=${Date.now()}`);
      console.log("new heatmap")

    } catch (error) {
      console.error('Error fetching search results:', error);
    }
  };
  

  // Toggle dropdown visibility
  const toggleDropdown = (dropdown) => {
    setActiveDropdown(activeDropdown === dropdown ? null : dropdown);
  };

  return (
    <div className={styles.dropdownContainer}>
      <button onClick={() => toggleDropdown('startpoint')} className={styles.dropdown}>
        {selectedStartStop.name}
      </button>

      {activeDropdown === 'startpoint' && (
        <div className={styles.dropdownContent}>
         {stopNames && stopNames.length > 0 ? ( stopNames.map((stopName, index) => ( 
          <a key={index} href={`#${index}`} onClick={() => 
            handleSelectStop(stopName.id, stopName.name, stopName.lat, stopName.lon, "start")}
          > 
          {stopName.name} {stopName.type?.toUpperCase()} </a> )) ) : ( <p>No available endpoints</p> )}
        </div>
      )}

      {/* TURNED OFF */}
      {/* <button onClick={() => toggleDropdown('endpoint')} className={styles.dropdown}>
        Endpoint
      </button> */}
      
      {/* {activeDropdown === 'endpoint' && ( 
        <div className={styles.dropdownContent} >
         {stopNames && stopNames.length > 0 ? ( stopNames.map((stopName, index) => ( <a key={index} href={`#${index}`} onClick={() => handleSelectStop(stop, 'end')}> {stopName.name} {stopName.type?.toUpperCase()} </a> )) ) : ( <p>No available endpoints</p> )}
        </div>
      )} */}
      
      <div className={styles.searchContainer}>
        <DatetimeComponent selectedDateTime={selectedDateTime} setSelectedDateTime={setSelectedDateTime}/>
        <button type="button" className={stylesButton.search} onClick={handleSearch}>
          Search
        </button>
      </div>
    </div>
  );
};

export default DropdownButton;
