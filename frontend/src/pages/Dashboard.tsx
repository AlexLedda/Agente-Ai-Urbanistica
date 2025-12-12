import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { FileUploader } from '../components/FileUploader';
import { ChatAssistant } from '../components/ChatAssistant';
import {
    MessageSquare,
    Files,
    Settings,
    LogOut,
    Menu,
    X
} from 'lucide-react';

export const Dashboard = () => {
    const { logout, username, token } = useAuth();
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [activeTab, setActiveTab] = useState<'chat' | 'upload' | 'settings'>('upload');
    const [recentFiles, setRecentFiles] = useState<any[]>([]);

    const fetchFiles = async () => {
        try {
            // Import dinamico di axios o uso di quello globale se configurato
            // Per semplicità uso fetch con il token
            const response = await fetch('/api/ingestion/files', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setRecentFiles(data);
            }
        } catch (error) {
            console.error("Errore recupero file:", error);
        }
    };

    useEffect(() => {
        if (activeTab === 'upload') {
            fetchFiles();
        }
    }, [activeTab]);

    const navItems = [
        { id: 'chat', label: 'Chat Assistant', icon: MessageSquare },
        { id: 'upload', label: 'Gestione File', icon: Files },
        { id: 'settings', label: 'Impostazioni', icon: Settings },
    ];

    return (
        <div className="flex h-screen bg-gray-900 text-white overflow-hidden">
            {/* Sidebar - Desktop */}
            <aside
                className={`${isSidebarOpen ? 'w-64' : 'w-20'
                    } bg-gray-800 border-r border-gray-700 transition-all duration-300 hidden md:flex flex-col`}
            >
                <div className="p-4 flex items-center justify-between">
                    {isSidebarOpen && <h1 className="font-bold text-xl text-blue-400">UrbanAI</h1>}
                    <button
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        className="p-2 hover:bg-gray-700 rounded-lg"
                    >
                        {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                </div>

                <nav className="flex-1 px-2 py-4 space-y-2">
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id as any)}
                            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${activeTab === item.id
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                                }`}
                        >
                            <item.icon size={20} />
                            {isSidebarOpen && <span>{item.label}</span>}
                        </button>
                    ))}
                </nav>

                <div className="p-4 border-t border-gray-700">
                    <div className={`flex items-center ${isSidebarOpen ? 'space-x-3' : 'justify-center'}`}>
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 flex items-center justify-center font-bold">
                            {username?.[0].toUpperCase()}
                        </div>
                        {isSidebarOpen && (
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium truncate">{username}</p>
                                <button
                                    onClick={logout}
                                    className="text-xs text-gray-400 hover:text-red-400 flex items-center mt-1"
                                >
                                    <LogOut size={12} className="mr-1" /> Logout
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col h-screen overflow-hidden">
                {/* Header - Mobile Only */}
                <header className="md:hidden bg-gray-800 p-4 flex items-center justify-between border-b border-gray-700">
                    <h1 className="font-bold text-lg">UrbanAI</h1>
                    <button onClick={logout}><LogOut size={20} /></button>
                </header>

                <div className="flex-1 overflow-auto p-4 md:p-8">
                    <div className="max-w-5xl mx-auto">
                        {activeTab === 'chat' && <ChatAssistant />}

                        {activeTab === 'upload' && (
                            <div className="space-y-6">
                                <div className="flex items-center justify-between">
                                    <h2 className="text-2xl font-bold">Gestione Normative</h2>
                                    <span className="bg-blue-500/10 text-blue-400 text-xs px-2 py-1 rounded border border-blue-500/20">
                                        Supporto PDF
                                    </span>
                                </div>

                                {/* Normativa Nazionale */}
                                <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                                    <div className="p-4 bg-gray-750 border-b border-gray-700 flex justify-between items-center">
                                        <h3 className="text-lg font-semibold text-white">Normativa Nazionale</h3>
                                    </div>
                                    <div className="p-6">
                                        <FileUploader
                                            onUploadSuccess={fetchFiles}
                                            initialLocation={{
                                                region: '',
                                                province: '',
                                                municipality: '',
                                                normative_level: 'nazionale'
                                            }}
                                            fixedLevel={false} // Allow seeing the selector but it will default to Nazionale
                                        />
                                    </div>
                                </div>

                                {/* Normativa Regionale */}
                                <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                                    <div className="p-4 bg-gray-750 border-b border-gray-700 flex justify-between items-center">
                                        <h3 className="text-lg font-semibold text-white">Normativa Regionale</h3>
                                    </div>
                                    <div className="p-6">
                                        <div className="mb-4 text-sm text-gray-400">
                                            Seleziona la regione per caricare le leggi regionali specifiche.
                                        </div>
                                        <FileUploader
                                            onUploadSuccess={fetchFiles}
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
                                <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                                    <div className="p-4 bg-gray-750 border-b border-gray-700 flex justify-between items-center">
                                        <h3 className="text-lg font-semibold text-white">Normativa Provinciale</h3>
                                    </div>
                                    <div className="p-6">
                                        <div className="mb-4 text-sm text-gray-400">
                                            Seleziona provincia per i regolamenti provinciali.
                                        </div>
                                        <FileUploader
                                            onUploadSuccess={fetchFiles}
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
                                <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                                    <div className="p-4 bg-gray-750 border-b border-gray-700 flex justify-between items-center">
                                        <h3 className="text-lg font-semibold text-white">Normativa Comunale</h3>
                                    </div>
                                    <div className="p-6">
                                        <div className="mb-4 text-sm text-gray-400">
                                            Seleziona il comune per caricare PRG, NTA e regolamenti edilizi.
                                        </div>
                                        <FileUploader
                                            onUploadSuccess={fetchFiles}
                                            initialLocation={{
                                                region: '',
                                                province: '',
                                                municipality: '',
                                                normative_level: 'comunale'
                                            }}
                                        />
                                    </div>
                                </div>

                                <div className="mt-8">
                                    <h3 className="text-lg font-semibold mb-4 text-gray-300">File Recenti (Tutti i livelli)</h3>
                                    {recentFiles.length === 0 ? (
                                        <div className="bg-gray-800 rounded-xl border border-gray-700 p-8 text-center text-gray-500">
                                            Nessun file caricato di recente.
                                        </div>
                                    ) : (
                                        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                                            <table className="w-full text-left text-sm text-gray-400">
                                                <thead className="bg-gray-700/50 text-gray-200">
                                                    <tr>
                                                        <th className="px-6 py-3 font-medium">Nome File</th>
                                                        <th className="px-6 py-3 font-medium">Livello</th>
                                                        <th className="px-6 py-3 font-medium">Territorio</th>
                                                        <th className="px-6 py-3 font-medium text-right">Dimensione</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-gray-700">
                                                    {recentFiles.map((file, idx) => (
                                                        <tr key={idx} className="hover:bg-gray-700/30 transition-colors">
                                                            <td className="px-6 py-4 font-medium text-white flex items-center">
                                                                <Files className="w-4 h-4 mr-2 text-blue-400" />
                                                                {file.name}
                                                            </td>
                                                            <td className="px-6 py-4 capitalize">
                                                                {file.normative_level || 'N/A'}
                                                            </td>
                                                            <td className="px-6 py-4">
                                                                {file.municipality || file.province || file.region || 'Italia'}
                                                            </td>
                                                            <td className="px-6 py-4 text-right">
                                                                {(file.size / 1024 / 1024).toFixed(2)} MB
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                        {activeTab === 'settings' && (
                            <div className="text-center py-20">
                                <Settings className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                                <h2 className="text-2xl font-bold text-gray-500">Impostazioni</h2>
                                <p className="text-gray-600">Configurazione account e API.</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};
