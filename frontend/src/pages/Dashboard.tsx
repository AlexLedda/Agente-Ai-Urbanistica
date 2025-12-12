import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { ChatAssistant } from '../components/ChatAssistant';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileNav } from '../components/layout/MobileNav';
import { NormativeSection } from '../components/dashboard/NormativeSection';
import { RecentFiles } from '../components/dashboard/RecentFiles';
import { SettingsSection } from '../components/dashboard/SettingsSection';
import { LogOut } from 'lucide-react';
import NormativeMap from '../components/map/NormativeMap';

export const Dashboard = () => {
    const { logout, username, token } = useAuth();
    const { theme, setTheme } = useTheme();
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [activeTab, setActiveTab] = useState<'chat' | 'upload' | 'settings'>('upload');
    const [recentFiles, setRecentFiles] = useState<any[]>([]);

    // Context state for ChatAssistant
    const [chatContext, setChatContext] = useState<{
        region?: string;
        province?: string;
        municipality?: string;
    } | undefined>(undefined);

    const handleMapLocationSelect = (location: any) => {
        // Map backend location data to ChatAssistant context
        setChatContext({
            municipality: location.name.replace("Comune di ", ""),
            region: "Lazio", // Default or extract from data if available
            province: "Viterbo" // Default or extract
        });
        setActiveTab('chat');
    };

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

    return (
        <div className="flex h-screen bg-gray-900 text-white overflow-hidden bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800">
            {/* Sidebar - Desktop */}
            <Sidebar
                isOpen={isSidebarOpen}
                setIsOpen={setIsSidebarOpen}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                username={username}
                logout={logout}
            />

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

                <div className="flex-1 overflow-auto p-4 md:p-8 relative z-10 scroll-smooth pb-20 md:pb-8">
                    <div className="max-w-6xl mx-auto">
                        {activeTab === 'chat' && <ChatAssistant initialContext={chatContext} />}

                        {activeTab === 'upload' && (
                            <>
                                <div className="mb-8">
                                    <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                                        Mappa Normativa
                                    </h2>
                                    <NormativeMap onLocationSelect={handleMapLocationSelect} />
                                </div>
                                <NormativeSection onUploadSuccess={fetchFiles} />
                                <RecentFiles files={recentFiles} />
                            </>
                        )}

                        {activeTab === 'settings' && (
                            <SettingsSection
                                theme={theme}
                                setTheme={setTheme}
                                username={username}
                                logout={logout}
                            />
                        )}
                    </div>
                </div>

                {/* Mobile Bottom Navigation */}
                <MobileNav activeTab={activeTab} setActiveTab={setActiveTab} />
            </main>
        </div>
    );
};
