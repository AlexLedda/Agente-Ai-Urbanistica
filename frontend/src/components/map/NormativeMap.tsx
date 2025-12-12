import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import axios from 'axios';
import L from 'leaflet';

// Fix for default marker icon in React-Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface Location {
    id: string;
    name: string;
    level: string;
    coordinates: {
        lat: number;
        lng: number;
    };
    metadata: {
        website?: string;
        has_prg: boolean;
    };
}

interface NormativeMapProps {
    onLocationSelect?: (location: Location) => void;
}

const NormativeMap = ({ onLocationSelect }: NormativeMapProps) => {
    const [locations, setLocations] = useState<Location[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLocations = async () => {
            try {
                // Use relative path or configurable API URL
                const response = await axios.get('http://localhost:8000/api/normative/locations');
                setLocations(response.data.locations);
            } catch (error) {
                console.error("Error fetching locations:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchLocations();
    }, []);

    if (loading) {
        return <div className="h-64 flex items-center justify-center bg-gray-100 rounded-lg">Caricamento mappa...</div>;
    }

    return (
        <div className="h-[500px] w-full rounded-xl overflow-hidden shadow-lg border border-gray-200 z-0">
            <MapContainer
                center={[42.3, 12.0]} // Focus on Central Italy/Lazio initially
                zoom={9}
                style={{ height: '100%', width: '100%' }}
                className="z-0"
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {locations.map((loc) => (
                    <Marker key={loc.id} position={[loc.coordinates.lat, loc.coordinates.lng]}>
                        <Popup>
                            <div className="p-1">
                                <h3 className="font-bold text-lg mb-1">{loc.name}</h3>
                                <p className="text-sm text-gray-600 mb-2 capitalize">Livello: {loc.level}</p>
                                {loc.metadata.has_prg && (
                                    <div className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded w-fit mb-2">
                                        PRG Disponibile
                                    </div>
                                )}
                                <button
                                    onClick={() => onLocationSelect && onLocationSelect(loc)}
                                    className="w-full bg-blue-600 text-white text-sm py-1 px-3 rounded hover:bg-blue-700 transition"
                                >
                                    Visualizza Normativa
                                </button>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
};

export default NormativeMap;
