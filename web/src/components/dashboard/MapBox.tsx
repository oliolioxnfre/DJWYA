"use client";

import React, { useEffect } from "react";
import { MapContainer, TileLayer, Marker, useMap, ZoomControl } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { FestivalData } from "@/components/dashboard/FestivalCard";

// Fix Leaflet icons
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const icon: any = typeof window !== "undefined" ? L.icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    tooltipAnchor: [16, -28],
    shadowSize: [41, 41]
}) : null;

const createPulseIcon = (matchScore: number) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    if (typeof window === "undefined") return null as any;

    // Change color based on match score
    const color = matchScore > 80 ? "#22c55e" : matchScore > 50 ? "#eab308" : "#ef4444";

    return L.divIcon({
        className: "custom-div-icon",
        html: `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px ${color};"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    });
};


// Component to handle map flying
function MapUpdater({ center, zoom, offsetY = 0 }: { center: [number, number] | null; zoom: number | null; offsetY?: number }) {
    const map = useMap();
    useEffect(() => {
        if (!center || center.length !== 2 || zoom === null) return;
        
        let targetLatLng = L.latLng(center[0], center[1]);
        
        if (offsetY !== 0) {
            // Project to pixels at target zoom, add offset, then unproject
            const targetPoint = map.project(targetLatLng, zoom);
            const offsetPoint = L.point(targetPoint.x, targetPoint.y + offsetY);
            targetLatLng = map.unproject(offsetPoint, zoom);
        }

        const currentCenter = map.getCenter();
        const distance = currentCenter.distanceTo(targetLatLng);

        // Smooth flying options based on distance (distance in meters)
        const flyOptions = {
            duration: distance > 2000000 ? 3 : distance > 500000 ? 2 : 1.5,
            easeLinearity: 0.25,
        };

        map.flyTo(targetLatLng, zoom, flyOptions);
    }, [center, zoom, map, offsetY]);
    return null;
}

export interface MapBoxProps {
    festivals: FestivalData[];
    selectedIndex: number;
    onSelectFestival: (index: number) => void;
}

export default function MapBox({ festivals, selectedIndex, onSelectFestival }: MapBoxProps) {
    const [hasCenteredInitial, setHasCenteredInitial] = React.useState(false);
    const defaultCenter: [number, number] = [39.8283, -98.5795]; // Center of US

    let activeCenter: [number, number] | null = null;
    let activeZoom: number | null = null;

    if (festivals.length > 0) {
        if (selectedIndex >= 0 && selectedIndex < festivals.length) {
            const fest = festivals[selectedIndex];
            if (fest.lat && fest.lng) {
                activeCenter = [fest.lat, fest.lng];
                activeZoom = 7; // Closer zoom for festival
            }
        } else if (selectedIndex === -1 && !hasCenteredInitial) {
            // Find bounding box for all festivals ONLY the first time
            const lats = festivals.map(f => f.lat).filter((l): l is number => l !== null);
            const lngs = festivals.map(f => f.lng).filter((l): l is number => l !== null);

            if (lats.length > 0 && lngs.length > 0) {
                const maxLat = Math.max(...lats);
                const minLat = Math.min(...lats);
                const maxLng = Math.max(...lngs);
                const minLng = Math.min(...lngs);

                const centerLat = (maxLat + minLat) / 2;
                const centerLng = (maxLng + minLng) / 2;

                activeCenter = [centerLat, centerLng];
                activeZoom = 4;
                setHasCenteredInitial(true);
            }
        }
    }

    return (
        <MapContainer
            center={defaultCenter}
            zoom={4}
            style={{ height: "100%", width: "100%", zIndex: 0 }}
            zoomControl={false}
            className="bg-[#0f1014]"
        >
            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            />
            <ZoomControl position="topright" />
            <MapUpdater 
                center={activeCenter} 
                zoom={activeZoom} 
                offsetY={selectedIndex >= 0 ? 120 : 0} 
            />

            {festivals.map((fest, idx) => {
                if (!fest.lat || !fest.lng) return null;
                const isSelected = selectedIndex === idx;
                const markerIcon = isSelected ? icon : createPulseIcon(fest.total_match);

                return (
                    <Marker
                        key={idx}
                        position={[fest.lat, fest.lng]}
                        icon={markerIcon}
                        eventHandlers={{
                            click: () => onSelectFestival(idx),
                        }}
                        zIndexOffset={isSelected ? 1000 : 0}
                    >
                    </Marker>
                );
            })}
        </MapContainer>
    );
}
