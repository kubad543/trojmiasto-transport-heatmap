// components/MapComponent.js

"use client";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { Marker, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import styles from "./styles/map.module.css";

const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false }
);
const ImageOverlay = dynamic(
  () => import("react-leaflet").then((mod) => mod.ImageOverlay),
  { ssr: false }
);

const MapComponent = ({selectedStartStop, setSelectedStartStop, heatmapUrl}) => {
  const [markerPosition, setMarkerPosition] = useState(null);
  const [selectedStopPosition, setSelectedStopPosition] = useState(null); 

  // when stop changes
  useEffect(() => {
    if (selectedStartStop && selectedStartStop.lat && selectedStartStop.lon) {
      setMarkerPosition([selectedStartStop.lat, selectedStartStop.lon]);
    }
  }, [selectedStartStop]);

  useEffect(() => {
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: "/marker-icon-2x.png",
      iconUrl: "/marker-icon.png",
      shadowUrl: "/marker-shadow.png",
    });
  }, []);

  const MapClickHandler = () => {
    useMapEvents({
      async click(e) {
        setMarkerPosition(e.latlng); 
        console.log("Kliknięto na mapę, współrzędne:", e.latlng); 
        try { 
          const response = await fetch('http://localhost:8000/get-nearest-stop', {
            method: 'POST', 
            headers: { 
              'Content-Type': 'application/json'
            }, 
            body: JSON.stringify({ 
              lat: e.latlng.lat,
              lng: e.latlng.lng
            })
          });
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
      
          const data = await response.json();
          console.log(data)
          setSelectedStartStop({id: data.id, name: data.name, lat: data.lat, lon: data.lng});
          setSelectedStopPosition({ lat: data.lat, lng: data.lng });
        } catch (error) {
          console.error('Error fetching search results:', error);
        }
      },
    });
    return null;
  };

  useEffect(() => {
    if (selectedStopPosition) {
      setMarkerPosition(selectedStopPosition);
    }
  }, [selectedStopPosition]);

  return (
    <div className={styles.mapCont}>
      <MapContainer
        center={[54.3564194, 18.6530101]}
        zoom={11}
        className="h-full"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />

        {/* Nakładka heatmap */}
        <ImageOverlay
          url={heatmapUrl}
          bounds={[
            [54.229, 18.11024],
            [54.64288, 19.165],
          ]} // Zakres geograficzny pokrywający heatmapę
          opacity={0.5} // Ustawienie przezroczystości nakładki
        />

        <MapClickHandler />

        {markerPosition && <Marker position={markerPosition} />}

        
      </MapContainer>
    </div>
  );
};

export default MapComponent;
