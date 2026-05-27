import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, GeoJSON, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import sectionsData from '../data/southlea_data.json';
import facilitiesData from '../data/points.json';

const pointInPolygon = (point, vs) => {
  let x = point[0], y = point[1];
  let inside = false;
  for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
    let xi = vs[i][0], yi = vs[i][1];
    let xj = vs[j][0], yj = vs[j][1];
    let intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
};

// Custom leaf icon fix for default layers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// FIXED: Handles both 'select' and 'pinpoint' string states smoothly
function LocationMarker({ selectedLocation, setSelectedLocation, mapMode, sectionsData }) {
  useMapEvents({
    click(e) {
      if (mapMode === 'select' || mapMode === 'pinpoint') {
        const clickedPt = [e.latlng.lng, e.latlng.lat]; // GeoJSON format uses [lng, lat]
        let isInsideBounds = false;

        if (sectionsData && sectionsData.features) {
          for (let feature of sectionsData.features) {
            const geomType = feature.geometry.type;
            const coords = feature.geometry.coordinates;

            if (geomType === 'Polygon') {
              if (pointInPolygon(clickedPt, coords[0])) {
                isInsideBounds = true;
                break;
              }
            } else if (geomType === 'MultiPolygon') {
              for (let poly of coords) {
                if (pointInPolygon(clickedPt, poly[0])) {
                  isInsideBounds = true;
                  break;
                }
              }
            }
            if (isInsideBounds) break;
          }
        }

        if (isInsideBounds) {
          setSelectedLocation(e.latlng);
        } else {
          alert("❌ Boundary Error: The selected point is outside the allowable project boundaries! Please drop your marker pin within a valid shaded sector.");
        }
      }
    },
  });
  return selectedLocation ? <Marker position={selectedLocation}></Marker> : null;
}

function MapViewer({ selectedLocation, setSelectedLocation, mapMode, radius }) {
  const southleaParkCoords = [-17.962, 30.982];
  
  // Basemap State Controller
  const [basemap, setBasemap] = useState('dark');

  const basemapUrls = {
    dark: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    light: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    satellite: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
  };

  const onEachSection = (feature, layer) => {
    if (feature.properties) {
      const pop = feature.properties.Estimated_Population || "N/A";
      const influence = feature.properties["Shopping_Centre of influence"] || "N/A";
      layer.bindPopup(`<strong>Zone Metrics</strong><br/>Est. Population: ${pop}<br/>Influence Hub: ${influence}`);
    }
  };

  const onEachFacility = (feature, layer) => {
    if (feature.properties) {
      const name = feature.properties.name || "Unnamed Infrastructure Point";
      const type = feature.properties.class || "General Business Node";

      const tooltipHTML = `
        <div style="font-family: sans-serif; padding: 2px 4px; font-size: 12px; color: #333;">
          <strong>🏢 ${name}</strong><br/>
          <span style="color: #6b7280; font-size: 11px;">Classification: ${type.replace('_', ' ')}</span>
        </div>
      `;

      layer.bindTooltip(tooltipHTML, {
        permanent: false,
        direction: 'top',
        sticky: true,
        opacity: 0.95
      });
    }
  };

  const renderFacilityPoint = (feature, latlng) => {
    let markerColor = '#3b82f6'; 
    if (feature.properties.class === 'church') markerColor = '#a855f7';
    if (feature.properties.class === 'school' || feature.properties.class === 'secondary_school') markerColor = '#f59e0b';

    const geoMarkerOptions = {
      radius: 6,
      fillColor: markerColor,
      color: '#ffffff',
      weight: 1,
      opacity: 1,
      fillOpacity: 0.8
    };
    return L.circleMarker(latlng, geoMarkerOptions);
  };

  return (
    <div style={{ height: '100%', width: '100%', position: 'relative' }}>
      
      {/* Floating Basemap Selector UI Control Widget */}
      <div style={{ position: 'absolute', bottom: '25px', left: '25px', zIndex: 1000, backgroundColor: '#1f2937', padding: '10px', borderRadius: '8px', border: '1px solid #4b5563', display: 'flex', gap: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.3)' }}>
        <button onClick={() => setBasemap('dark')} style={{ padding: '6px 12px', fontSize: '12px', fontWeight: 'bold', border: 'none', borderRadius: '4px', cursor: 'pointer', backgroundColor: basemap === 'dark' ? '#3b82f6' : '#374151', color: 'white' }}>Dark Mode</button>
        <button onClick={() => setBasemap('light')} style={{ padding: '6px 12px', fontSize: '12px', fontWeight: 'bold', border: 'none', borderRadius: '4px', cursor: 'pointer', backgroundColor: basemap === 'light' ? '#3b82f6' : '#374151', color: 'white' }}>White Mode</button>
        <button onClick={() => setBasemap('satellite')} style={{ padding: '6px 12px', fontSize: '12px', fontWeight: 'bold', border: 'none', borderRadius: '4px', cursor: 'pointer', backgroundColor: basemap === 'satellite' ? '#3b82f6' : '#374151', color: 'white' }}>Satellite Hybrid</button>
      </div>

      {/* Map Legend Overlay */}
      <div style={{ position: 'absolute', bottom: '25px', right: '25px', zIndex: 1000, backgroundColor: '#1f2937', color: 'white', padding: '12px', borderRadius: '8px', fontSize: '13px', border: '1px solid #4b5563', display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <div style={{ fontWeight: 'bold', marginBottom: '4px', borderBottom: '1px solid #4b5563', paddingBottom: '4px' }}>Legend</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><span style={{ width: '12px', height: '12px', backgroundColor: '#f59e0b', borderRadius: '50%', display: 'inline-block' }}></span> Academic Centres</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><span style={{ width: '12px', height: '12px', backgroundColor: '#a855f7', borderRadius: '50%', display: 'inline-block' }}></span> Places of Worship</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><span style={{ width: '12px', height: '12px', backgroundColor: '#3b82f6', opacity: 0.3, border: '2px solid #3b82f6', display: 'inline-block' }}></span> Zonal Boundaries</div>
      </div>

      <MapContainer center={southleaParkCoords} zoom={14} style={{ height: '100%', width: '100%', backgroundColor: '#111827' }}>
        <TileLayer attribution='&copy; ESRI & CARTO Spatial' url={basemapUrls[basemap]} />
        
        {/* Disables layer interactivity dynamically during pinpointing so GeoJSON lines don't block clicks */}
        <GeoJSON key={`sections-${mapMode}`} data={sectionsData} onEachFeature={onEachSection} style={{ color: '#3b82f6', weight: 2, fillOpacity: 0.1 }} interactive={mapMode === 'explore'} />
        <GeoJSON key={`facilities-${mapMode}`} data={facilitiesData} pointToLayer={renderFacilityPoint} onEachFeature={onEachFacility} interactive={mapMode === 'explore'} />
        
        {/* FIXED: Injected the local sectionsData variable loop directly here */}
        <LocationMarker selectedLocation={selectedLocation} setSelectedLocation={setSelectedLocation} mapMode={mapMode} sectionsData={sectionsData} />
        
        {selectedLocation && (
          <Circle center={selectedLocation} radius={radius} pathOptions={{ color: '#10b981', fillColor: '#10b981', fillOpacity: 0.15, weight: 1.5 }} />
        )}
      </MapContainer>
    </div>
  );
}

export default MapViewer;