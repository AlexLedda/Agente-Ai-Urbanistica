import React, { useState, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

interface LocationData {
    nome: string;
    codice: string;
    regione: {
        nome: string;
        codice: string;
    };
    provincia: {
        nome: string;
        codice: string;
    };
    sigla: string;
}

interface LocationSelectorProps {
    onLocationSelect: (location: {
        region: string;
        province: string;
        municipality: string;
        normative_level: string;
    }) => void;
    forcedLevel?: 'nazionale' | 'regionale' | 'provinciale' | 'comunale';
}

const LocationSelector: React.FC<LocationSelectorProps> = ({ onLocationSelect }) => {
    const [data, setData] = useState<LocationData[]>([]);
    const [loading, setLoading] = useState(true);

    const [selectedCountry, setSelectedCountry] = useState('Italia'); // Always default to Italia for now
    const [selectedRegion, setSelectedRegion] = useState('');
    const [selectedProvince, setSelectedProvince] = useState('');
    const [selectedMunicipality, setSelectedMunicipality] = useState('');

    const [regions, setRegions] = useState<string[]>([]);
    const [provinces, setProvinces] = useState<string[]>([]);
    const [municipalities, setMunicipalities] = useState<string[]>([]);

    useEffect(() => {
        fetch('/data/comuni.json')
            .then(res => res.json())
            .then((jsonData: LocationData[]) => {
                setData(jsonData);
                const uniqueRegions = Array.from(new Set(jsonData.map(item => item.regione.nome))).sort();
                setRegions(uniqueRegions);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error loading location data:", err);
                setLoading(false);
            });
    }, []);

    // Filter provinces when region changes
    useEffect(() => {
        if (selectedRegion) {
            const filteredProvinces = Array.from(new Set(
                data
                    .filter(item => item.regione.nome === selectedRegion)
                    .map(item => item.provincia.nome)
            )).sort();
            setProvinces(filteredProvinces);
            // Only reset if strict change
        } else {
            setProvinces([]);
        }
    }, [selectedRegion, data]);

    // Filter municipalities when province changes
    useEffect(() => {
        if (selectedProvince) {
            const filteredMunicipalities = data
                .filter(item => item.regione.nome === selectedRegion && item.provincia.nome === selectedProvince)
                .map(item => item.nome)
                .sort();
            setMunicipalities(filteredMunicipalities);
        } else {
            setMunicipalities([]);
        }
    }, [selectedProvince, selectedRegion, data]);

    // Update parent on selection changes
    useEffect(() => {
        // Determine effective level
        let level = 'nazionale';
        if (selectedMunicipality) level = 'comunale';
        else if (selectedProvince) level = 'provinciale';
        else if (selectedRegion) level = 'regionale';

        onLocationSelect({
            region: selectedRegion,
            province: selectedProvince,
            municipality: selectedMunicipality,
            normative_level: level
        });
    }, [selectedCountry, selectedRegion, selectedProvince, selectedMunicipality]);

    if (loading) return <div className="text-sm text-gray-500">Caricamento dati territoriali...</div>;

    return (
        <div className="space-y-4 mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Seleziona Ambito Territoriale</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Country Selector */}
                <div className="relative">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Nazione</label>
                    <select
                        value={selectedCountry}
                        onChange={(e) => {
                            setSelectedCountry(e.target.value);
                            if (e.target.value !== 'Italia') {
                                setSelectedRegion('');
                                setSelectedProvince('');
                                setSelectedMunicipality('');
                            }
                        }}
                        className="block w-full appearance-none bg-white border border-gray-300 hover:border-gray-400 px-4 py-2 pr-8 rounded leading-tight focus:outline-none focus:shadow-outline text-sm text-gray-900"
                    >
                        <option value="">Seleziona Nazione</option>
                        <option value="Italia">Italia</option>
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 mt-5">
                        <ChevronDown size={14} />
                    </div>
                </div>

                {/* Region Selector */}
                <div className="relative">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Regione</label>
                    <select
                        value={selectedRegion}
                        onChange={(e) => setSelectedRegion(e.target.value)}
                        disabled={selectedCountry !== 'Italia'}
                        className="block w-full appearance-none bg-white border border-gray-300 hover:border-gray-400 px-4 py-2 pr-8 rounded leading-tight focus:outline-none focus:shadow-outline text-sm disabled:bg-gray-100 disabled:text-gray-400 text-gray-900"
                    >
                        <option value="">Seleziona Regione</option>
                        {regions.map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 mt-5">
                        <ChevronDown size={14} />
                    </div>
                </div>

                {/* Province Selector */}
                <div className="relative">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Provincia</label>
                    <select
                        value={selectedProvince}
                        onChange={(e) => setSelectedProvince(e.target.value)}
                        disabled={!selectedRegion}
                        className="block w-full appearance-none bg-white border border-gray-300 hover:border-gray-400 px-4 py-2 pr-8 rounded leading-tight focus:outline-none focus:shadow-outline text-sm disabled:bg-gray-100 disabled:text-gray-400 text-gray-900"
                    >
                        <option value="">Seleziona Provincia</option>
                        {provinces.map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 mt-5">
                        <ChevronDown size={14} />
                    </div>
                </div>

                {/* Municipality Selector */}
                <div className="relative">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Comune</label>
                    <select
                        value={selectedMunicipality}
                        onChange={(e) => setSelectedMunicipality(e.target.value)}
                        disabled={!selectedProvince}
                        className="block w-full appearance-none bg-white border border-gray-300 hover:border-gray-400 px-4 py-2 pr-8 rounded leading-tight focus:outline-none focus:shadow-outline text-sm disabled:bg-gray-100 disabled:text-gray-400 text-gray-900"
                    >
                        <option value="">Seleziona Comune</option>
                        {municipalities.map(m => <option key={m} value={m}>{m}</option>)}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 mt-5">
                        <ChevronDown size={14} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LocationSelector;
