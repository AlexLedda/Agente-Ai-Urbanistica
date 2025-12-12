import {
    MessageSquare,
    Files,
    Settings,
    LogOut,
    Menu,
    X
} from 'lucide-react';

interface SidebarProps {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
    activeTab: 'chat' | 'upload' | 'settings';
    setActiveTab: (tab: 'chat' | 'upload' | 'settings') => void;
    username: string | null;
    logout: () => void;
}

export const Sidebar = ({ isOpen, setIsOpen, activeTab, setActiveTab, username, logout }: SidebarProps) => {
    const navItems = [
        { id: 'chat', label: 'Chat Assistant', icon: MessageSquare },
        { id: 'upload', label: 'Gestione File', icon: Files },
        { id: 'settings', label: 'Impostazioni', icon: Settings },
    ];

    return (
        <aside
            className={`${isOpen ? 'w-64' : 'w-20'
                } bg-gray-800/80 backdrop-blur-xl border-r border-gray-700/50 transition-all duration-300 hidden md:flex flex-col relative z-20`}
        >
            <div className="p-6 flex items-center justify-between">
                {isOpen && (
                    <h1 className="font-bold text-2xl bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                        UrbanAI
                    </h1>
                )}
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors"
                >
                    {isOpen ? <X size={20} /> : <Menu size={20} />}
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
                        {isOpen && <span className="font-medium">{item.label}</span>}
                    </button>
                ))}
            </nav>

            <div className="p-4 border-t border-gray-700/50">
                <div className={`flex items-center ${isOpen ? 'space-x-3' : 'justify-center'}`}>
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center font-bold shadow-lg shadow-primary/20">
                        {username?.[0].toUpperCase()}
                    </div>
                    {isOpen && (
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
    );
};
