// pages/search.tsx
"use client";

import React, { useState } from 'react';
import styles from "../../components/styles/bg.module.css";
import MapComponent  from "../../components/Map"; 
import SearchMenu from "../../components/SearchDropDown"

export default function Search() {
  const [startStop, setStartStop] = useState({
    name: "Startpoint",
    lat: null,
    lon: null,
    id: 0}
  );
  const [heatmap, setHeatMap] = useState("/heatmap.svg");

  return (
    <div className={styles.searchBg}>
      <main className="flex h-screen">
        <SearchMenu selectedStartStop={startStop} setSelectedStartStop={setStartStop} setHeatmapUrl = {setHeatMap} />
        <div className="w-3/5 h-full">
        <MapComponent selectedStartStop={startStop} setSelectedStartStop={setStartStop} heatmapUrl={heatmap} /> 
        </div>
      </main>
    </div>
  );
}