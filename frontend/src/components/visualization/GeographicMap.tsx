import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { GeoLocation } from '../../types';

interface GeographicMapProps {
  location: GeoLocation;
  spatialExtent?: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  title?: string;
  height?: string;
}

export const GeographicMap: React.FC<GeographicMapProps> = ({
  location,
  spatialExtent,
  title,
  height = '310px',
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [location.lat, location.lng],
        zoom: 10,
        zoomControl: false,
        attributionControl: false,
      });

      // CARTO Basemaps require an API key to serve tiles without "API KEY REQUIRED" watermarks.
      // Configured via VITE_CARTO_API_KEY. When absent, falls back to OpenStreetMap so watermarks never appear.
      const cartoApiKey = (import.meta.env.VITE_CARTO_API_KEY || '').trim();
      const tileUrl = cartoApiKey
        ? `https://{s}.basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}{r}.png?key=${encodeURIComponent(cartoApiKey)}`
        : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

      L.tileLayer(tileUrl, {
        maxZoom: 19,
        subdomains: cartoApiKey ? 'abcd' : 'abc',
      }).addTo(map);

      L.control.zoom({ position: 'topright' }).addTo(map);

      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;
    map.setView([location.lat, location.lng], 10);

    map.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.Rectangle) {
        map.removeLayer(layer);
      }
    });

    // Minimal square pinpoint marker
    const markerHtml = `
      <div style="
        width: 10px;
        height: 10px;
        background-color: #18181B;
        border: 1px solid #FFFFFF;
        box-shadow: 0 0 0 1px #71717A;
      "></div>
    `;

    const customIcon = L.divIcon({
      html: markerHtml,
      className: 'point-marker',
      iconSize: [10, 10],
      iconAnchor: [5, 5],
    });

    const marker = L.marker([location.lat, location.lng], { icon: customIcon }).addTo(map);
    marker.bindTooltip(
      `${location.name} (${location.lat.toFixed(4)}°, ${location.lng.toFixed(4)}°)`,
      { direction: 'top', offset: [0, -6] }
    );

    if (spatialExtent) {
      const bounds: L.LatLngBoundsExpression = [
        [spatialExtent.south, spatialExtent.west],
        [spatialExtent.north, spatialExtent.east],
      ];
      L.rectangle(bounds, {
        color: '#2563EB',
        weight: 1,
        fillColor: '#2563EB',
        fillOpacity: 0.04,
        dashArray: '3, 3',
      }).addTo(map);
    }
  }, [location, spatialExtent]);

  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div
      style={{
        border: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-surface)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div
        style={{
          padding: '6px 10px',
          backgroundColor: 'var(--color-surface)',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '11px',
        }}
      >
        <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
          {title || `Grid Cell: ${location.name}`}
        </span>
        <span className="tabular-nums" style={{ color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
          {location.lat.toFixed(4)}°, {location.lng.toFixed(4)}° (WGS84)
        </span>
      </div>

      <div ref={mapContainerRef} style={{ height, width: '100%', position: 'relative' }} />

      <div
        style={{
          padding: '4px 10px',
          backgroundColor: 'var(--color-bg)',
          borderTop: '1px solid var(--color-border)',
          display: 'flex',
          gap: '12px',
          alignItems: 'center',
          fontSize: '10px',
          color: 'var(--color-text-muted)',
        }}
      >
        <span>Black Square: Target Point Coordinate</span>
        <span>•</span>
        <span>Dashed Rectangle: Bounding Spatial Box</span>
      </div>
    </div>
  );
};
