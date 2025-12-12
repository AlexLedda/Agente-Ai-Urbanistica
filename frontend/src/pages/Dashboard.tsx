import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme, THEMES } from '../context/ThemeContext';
import { FileUploader } from '../components/FileUploader';
import { ChatAssistant } from '../components/ChatAssistant';
import {
    MessageSquare,
    Files,
    Settings,
    LogOut,
    Menu,
    X,
    Palette,
    Check
} from 'lucide-react';

export const Dashboard = () => {
    const { logout, username, token } = useAuth();
    const { theme, setTheme } = useTheme();
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [activeTab, setActiveTab] = useState<'chat' | 'upload' | 'settings'>('upload');
    const [recentFiles, setRecentFiles] = useState<any[]>([]);

    const fetchFiles = async () => {
        try {
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
        <div className="flex h-screen bg-gray-900 text-white overflow-hidden bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800">
            {/* Sidebar - Desktop */}
            <aside
                className={`${isSidebarOpen ? 'w-64' : 'w-20'
                    } bg-gray-800/80 backdrop-blur-xl border-r border-gray-700/50 transition-all duration-300 hidden md:flex flex-col relative z-20`}
            >
                <div className="p-6 flex items-center justify-between">
                    {isSidebarOpen && (
                        <h1 className="font-bold text-2xl bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                            UrbanAI
                        </h1>
                    )}
                    <button
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors"
                    >
                        {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                </div>

                <nav className="flex-1 px-3 py-6 space-y-2">
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id as any)}
                            className={`w-full flex items-center space-x-3 px-4 py-3.5 rounded-xl transition-all duration-200 group ${activeTab === item.id
                                    ? 'bg-gradient-to-r from-primary/20 to-primary/10 text-primary border border-primary/20'
                                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                                }`}
                        >
                            <item.icon
                                size={22}
                                className={`transition-colors ${activeTab === item.id ? 'text-primary' : 'text-gray-400 group-hover:text-white'
                                    }`}
                            />
                            {isSidebarOpen && <span className="font-medium">{item.label}</span>}
                        </button>
                    ))}
                </nav>

                <div className="p-4 border-t border-gray-700/50">
                    <div className={`flex items-center ${isSidebarOpen ? 'space-x-3' : 'justify-center'}`}>
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center font-bold shadow-lg shadow-primary/20">
                            {username?.[0].toUpperCase()}
                        </div>
                        {isSidebarOpen && (
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-semibold truncate text-gray-200">{username}</p>
                                <button
                                    onClick={logout}
                                    className="text-xs text-gray-400 hover:text-red-400 flex items-center mt-1 transition-colors"
                                >
                                    <LogOut size={12} className="mr-1" /> Logout
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
                {/* Background Glow Effects */}
                <div className="absolute top-0 left-0 w-96 h-96 bg-primary/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
                <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 pointer-events-none" />

                {/* Header - Mobile Only */}
                <header className="md:hidden bg-gray-900/90 backdrop-blur-md p-4 flex items-center justify-between border-b border-gray-800 z-20">
                    <h1 className="font-bold text-xl bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                        UrbanAI
                    </h1>
                    <button onClick={logout} className="text-gray-400"><LogOut size={20} /></button>
                </header>

                <div className="flex-1 overflow-auto p-4 md:p-8 relative z-10 scroll-smooth">
                    <div className="max-w-6xl mx-auto">
                        {activeTab === 'chat' && <ChatAssistant />}

                        {activeTab === 'upload' && (
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
                                                onUploadSuccess={fetchFiles}
                                                initialLocation={{
                                                    region: '',
                                                    province: '',
                                                    municipality: '',
                                                    normative_level: 'nazionale'
                                                }}
                                                fixedLevel={false}
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
                                </div>

                                <div className="mt-8">
                                    <h3 className="text-xl font-semibold mb-6 flex items-center text-gray-200">
                                        <Files className="mr-2 text-primary" size={24} />
                                        File Recenti
                                    </h3>
                                    {recentFiles.length === 0 ? (
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
                                                        {recentFiles.map((file, idx) => (
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
                            </div>
                        )}
                        {activeTab === 'settings' && (
                            <div className="glass-card p-8 animate-in fade-in zoom-in-95 duration-500">
                                <h2 className="text-2xl font-bold mb-6 flex items-center">
                                    <Settings className="mr-3 text-primary" />
                                    Impostazioni Applicazione
                                </h2>

                                <div className="space-y-8">
                                    <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700/50">
                                        <h3 className="text-lg font-semibold mb-4 flex items-center text-gray-200">
                                            <Palette className="mr-2 text-accent" size={20} />
                                            Aspetto e Temi
                                        </h3>
                                        <p className="text-gray-400 mb-6 text-sm">
                                            Personalizza l'interfaccia scegliendo uno dei temi disponibili. La scelta verrà salvata automaticamente.
                                        </p>

                                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                                            {THEMES.map((t) => (
                                                <button
                                                    key={t.id}
                                                    onClick={() => setTheme(t.id as any)}
                                                    className={`relative group overflow-hidden rounded-xl p-4 transition-all duration-300 border-2 text-left
                                                        ${theme === t.id
                                                            ? 'border-primary bg-gray-800 ring-2 ring-primary/20 shadow-lg shadow-primary/10'
                                                            : 'border-gray-700 bg-gray-900/50 hover:border-gray-600 hover:bg-gray-800'
                                                        }`}
                                                >
                                                    <div className={`w-full h-24 rounded-lg mb-4 ${t.color} bg-opacity-80 group-hover:bg-opacity-100 transition-all flex items-center justify-center`}>
                                                        {theme === t.id && (
                                                            <div className="bg-white/90 backdrop-blur rounded-full p-2 shadow-sm animate-in zoom-in">
                                                                <Check className="text-gray-900" size={20} />
                                                            </div>
                                                        )}
                                                    </div>
                                                    <div className="font-semibold text-gray-200 group-hover:text-white">{t.label}</div>
                                                    <div className="text-xs text-gray-500 mt-1">Tema {t.id}</div>
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700/50">
                                        <h3 className="text-lg font-semibold mb-4 text-gray-200">Account</h3>
                                        <div className="flex items-center space-x-4">
                                            <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-2xl font-bold shadow-lg">
                                                {username?.[0].toUpperCase()}
                                            </div>
                                            <div>
                                                <p className="text-white font-medium text-lg">{username}</p>
                                                <p className="text-gray-500 text-sm">Amministratore di Sistema</p>
                                            </div>
                                        </div>
                                        <div className="mt-6 pt-6 border-t border-gray-700/50">
                                            <button
                                                onClick={logout}
                                                className="px-4 py-2 bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 rounded-lg transition-colors text-sm font-medium flex items-center"
                                            >
                                                <LogOut size={16} className="mr-2" />
                                                Disconnetti Sessione
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};
