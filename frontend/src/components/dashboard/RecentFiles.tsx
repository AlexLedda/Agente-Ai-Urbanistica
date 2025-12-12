import { Files } from 'lucide-react';

interface RecentFilesProps {
    files: any[];
}

export const RecentFiles = ({ files }: RecentFilesProps) => {
    return (
        <div className="mt-8">
            <h3 className="text-xl font-semibold mb-6 flex items-center text-gray-200">
                <Files className="mr-2 text-primary" size={24} />
                File Recenti
            </h3>
            {files.length === 0 ? (
                <div className="glass-card p-12 text-center text-gray-500 flex flex-col items-center justify-center">
                    <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mb-4">
                        <Files className="text-gray-600" size={32} />
                    </div>
                    <p>Nessun documento caricato di recente.</p>
                </div>
            ) : (
                <div className="glass-card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-400">
                            <thead className="bg-gray-800/50 text-gray-200">
                                <tr>
                                    <th className="px-6 py-4 font-medium uppercase text-xs tracking-wider">Nome File</th>
                                    <th className="px-6 py-4 font-medium uppercase text-xs tracking-wider">Livello</th>
                                    <th className="px-6 py-4 font-medium uppercase text-xs tracking-wider">Territorio</th>
                                    <th className="px-6 py-4 font-medium uppercase text-xs tracking-wider text-right">Dimensione</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700/50">
                                {files.map((file, idx) => (
                                    <tr key={idx} className="hover:bg-white/5 transition-colors">
                                        <td className="px-6 py-4 font-medium text-white flex items-center">
                                            <div className="p-2 bg-primary/10 rounded-lg mr-3">
                                                <Files className="w-4 h-4 text-primary" />
                                            </div>
                                            {file.name}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium border
                                                ${file.normative_level === 'nazionale' ? 'bg-primary/10 text-primary border-primary/20' :
                                                    file.normative_level === 'regionale' ? 'bg-secondary/10 text-secondary border-secondary/20' :
                                                        'bg-gray-700 text-gray-300 border-gray-600'
                                                }`}>
                                                {file.normative_level || 'N/A'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            {file.municipality || file.province || file.region || 'Italia'}
                                        </td>
                                        <td className="px-6 py-4 text-right tabular-nums">
                                            {(file.size / 1024 / 1024).toFixed(2)} MB
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};
