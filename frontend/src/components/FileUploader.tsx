import React, { useCallback, useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, X } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import LocationSelector from './LocationSelector';

export const FileUploader = ({ onUploadSuccess }: { onUploadSuccess?: () => void }) => {
    const [dragActive, setDragActive] = useState(false);
    const [files, setFiles] = useState<File[]>([]);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [errorMessage, setErrorMessage] = useState('');
    const { token } = useAuth();

    const [selectedLocation, setSelectedLocation] = useState({
        region: '',
        province: '',
        municipality: '',
        normative_level: 'nazionale'
    });

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const droppedFiles = Array.from(e.dataTransfer.files).filter(
                file => file.type === 'application/pdf'
            );
            setFiles(prev => [...prev, ...droppedFiles]);
        }
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            const selectedFiles = Array.from(e.target.files).filter(
                file => file.type === 'application/pdf'
            );
            setFiles(prev => [...prev, ...selectedFiles]);
        }
    };

    const removeFile = (idx: number) => {
        setFiles(prev => prev.filter((_, i) => i !== idx));
    };

    const uploadFiles = async () => {
        if (files.length === 0) return;
        setUploading(true);
        setUploadStatus('idle');

        try {
            const formData = new FormData();
            files.forEach(file => {
                formData.append('files', file);
            });

            // Append metadata
            if (selectedLocation.region) formData.append('region', selectedLocation.region);
            if (selectedLocation.province) formData.append('province', selectedLocation.province);
            if (selectedLocation.municipality) formData.append('municipality', selectedLocation.municipality);
            formData.append('normative_level', selectedLocation.normative_level);

            await axios.post('/api/ingestion/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${token}`
                }
            });

            setUploadStatus('success');
            setFiles([]);
            if (onUploadSuccess) onUploadSuccess();
        } catch (error: any) {
            console.error(error);
            setUploadStatus('error');
            setErrorMessage(error.response?.data?.detail || error.message || "Errore sconosciuto");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto space-y-6">

            <LocationSelector onLocationSelect={setSelectedLocation} />

            <div
                className={`relative border-2 border-dashed rounded-xl p-8 transition-all duration-200 ease-in-out ${dragActive
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-gray-600 hover:border-gray-500 bg-gray-800/50'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <div className="text-center">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-700 mb-4">
                        <Upload className="w-6 h-6 text-blue-400" />
                    </div>
                    <h3 className="text-lg font-medium text-white mb-2">
                        Trascina qui i tuoi PDF
                    </h3>
                    <p className="text-gray-400 text-sm mb-4">
                        oppure clicca per selezionare
                    </p>

                    <input
                        type="file"
                        multiple
                        accept=".pdf"
                        className="hidden"
                        id="file-upload"
                        onChange={handleChange}
                    />
                    <label
                        htmlFor="file-upload"
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg cursor-pointer text-sm font-medium transition-colors"
                    >
                        Seleziona File
                    </label>
                </div>
            </div>

            {files.length > 0 && (
                <div className="mt-6 space-y-3">
                    {files.map((file, idx) => (
                        <div
                            key={idx}
                            className="flex items-center justify-between p-3 bg-gray-800 rounded-lg border border-gray-700"
                        >
                            <div className="flex items-center space-x-3">
                                <FileText className="w-5 h-5 text-gray-400" />
                                <div>
                                    <p className="text-sm font-medium text-white">{file.name}</p>
                                    <p className="text-xs text-gray-400">
                                        {(file.size / 1024 / 1024).toFixed(2)} MB
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => removeFile(idx)}
                                className="p-1 hover:bg-gray-700 rounded-full text-gray-400 hover:text-red-400"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    ))}

                    <div className="flex justify-end mt-4">
                        <button
                            onClick={uploadFiles}
                            disabled={uploading}
                            className={`px-6 py-2 rounded-lg font-medium text-white transition-all ${uploading
                                ? 'bg-blue-600/50 cursor-wait'
                                : 'bg-green-600 hover:bg-green-700'
                                }`}
                        >
                            {uploading ? 'Caricamento...' : `Carica ${files.length} file`}
                        </button>
                    </div>
                </div>
            )}

            {uploadStatus === 'success' && (
                <div className="mt-4 p-4 bg-green-500/10 border border-green-500/20 rounded-lg flex items-center text-green-400">
                    <CheckCircle className="w-5 h-5 mr-2" />
                    Upload completato con successo!
                </div>
            )}

            {uploadStatus === 'error' && (
                <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center text-red-400">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    {errorMessage || "Errore durante il caricamento."}
                </div>
            )}
        </div>
    );
};
