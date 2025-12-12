import { FileUploader } from '../FileUploader';

interface NormativeSectionProps {
    onUploadSuccess: () => void;
}

export const NormativeSection = ({ onUploadSuccess }: NormativeSectionProps) => {
    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                        Gestione Normative
                    </h2>
                    <p className="text-gray-400 mt-1">Carica e organizza i documenti normativi</p>
                </div>
                <span className="bg-primary/10 text-primary text-xs font-medium px-3 py-1.5 rounded-full border border-primary/20">
                    Supporto PDF & OCR
                </span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Normativa Nazionale */}
                <div className="glass-card overflow-hidden group hover:scale-[1.01] transition-transform">
                    <div className="p-4 border-b border-gray-700/50 bg-gradient-to-r from-gray-800/80 to-gray-800/40 flex justify-between items-center">
                        <h3 className="text-lg font-semibold text-white flex items-center">
                            <div className="w-2 h-8 bg-primary rounded-full mr-3" />
                            Normativa Nazionale
                        </h3>
                    </div>
                    <div className="p-6">
                        <FileUploader
                            onUploadSuccess={onUploadSuccess}
                            initialLocation={{
                                region: '',
                                province: '',
                                municipality: '',
                                normative_level: 'nazionale'
                            }}
                        />
                    </div>
                </div>

                {/* Normativa Regionale */}
                <div className="glass-card overflow-hidden group hover:scale-[1.01] transition-transform">
                    <div className="p-4 border-b border-gray-700/50 bg-gradient-to-r from-gray-800/80 to-gray-800/40 flex justify-between items-center">
                        <h3 className="text-lg font-semibold text-white flex items-center">
                            <div className="w-2 h-8 bg-secondary rounded-full mr-3" />
                            Normativa Regionale
                        </h3>
                    </div>
                    <div className="p-6">
                        <p className="mb-4 text-sm text-gray-400">
                            Archivio leggi regionali e piani territoriali.
                        </p>
                        <FileUploader
                            onUploadSuccess={onUploadSuccess}
                            initialLocation={{
                                region: '',
                                province: '',
                                municipality: '',
                                normative_level: 'regionale'
                            }}
                        />
                    </div>
                </div>

                {/* Normativa Provinciale */}
                <div className="glass-card overflow-hidden group hover:scale-[1.01] transition-transform">
                    <div className="p-4 border-b border-gray-700/50 bg-gradient-to-r from-gray-800/80 to-gray-800/40 flex justify-between items-center">
                        <h3 className="text-lg font-semibold text-white flex items-center">
                            <div className="w-2 h-8 bg-accent rounded-full mr-3" />
                            Normativa Provinciale
                        </h3>
                    </div>
                    <div className="p-6">
                        <p className="mb-4 text-sm text-gray-400">
                            Regolamenti di competenza provinciale.
                        </p>
                        <FileUploader
                            onUploadSuccess={onUploadSuccess}
                            initialLocation={{
                                region: '',
                                province: '',
                                municipality: '',
                                normative_level: 'provinciale'
                            }}
                        />
                    </div>
                </div>

                {/* Normativa Comunale */}
                <div className="glass-card overflow-hidden group hover:scale-[1.01] transition-transform">
                    <div className="p-4 border-b border-gray-700/50 bg-gradient-to-r from-gray-800/80 to-gray-800/40 flex justify-between items-center">
                        <h3 className="text-lg font-semibold text-white flex items-center">
                            <div className="w-2 h-8 bg-white/50 rounded-full mr-3" />
                            Normativa Comunale
                        </h3>
                    </div>
                    <div className="p-6">
                        <p className="mb-4 text-sm text-gray-400">
                            PRG, NTA, Regolamenti Edilizi comunali.
                        </p>
                        <FileUploader
                            onUploadSuccess={onUploadSuccess}
                            initialLocation={{
                                region: '',
                                province: '',
                                municipality: '',
                                normative_level: 'comunale'
                            }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};
