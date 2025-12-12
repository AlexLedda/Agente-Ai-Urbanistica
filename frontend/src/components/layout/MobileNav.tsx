import {
    MessageSquare,
    Files,
    Settings,
} from 'lucide-react';

interface MobileNavProps {
    activeTab: 'chat' | 'upload' | 'settings';
    setActiveTab: (tab: 'chat' | 'upload' | 'settings') => void;
}

export const MobileNav = ({ activeTab, setActiveTab }: MobileNavProps) => {
    const navItems = [
        { id: 'chat', label: 'Chat Assistant', icon: MessageSquare },
        { id: 'upload', label: 'Gestione File', icon: Files },
        { id: 'settings', label: 'Impostazioni', icon: Settings },
    ];

    return (
        <div className="md:hidden absolute bottom-0 left-0 right-0 bg-gray-900/90 backdrop-blur-lg border-t border-gray-800 p-2 z-30 pb-safe">
            <div className="flex justify-around items-center">
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id as any)}
                        className={`flex flex-col items-center p-2 rounded-lg transition-colors ${activeTab === item.id
                            ? 'text-primary bg-primary/10'
                            : 'text-gray-400 hover:text-white'
                            }`}
                    >
                        <item.icon size={20} />
                        <span className="text-[10px] mt-1 font-medium">{item.label}</span>
                    </button>
                ))}
            </div>
        </div>
    );
};
