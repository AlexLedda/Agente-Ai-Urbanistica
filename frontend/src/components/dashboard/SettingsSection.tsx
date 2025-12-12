import { Settings, Palette, Check, LogOut } from 'lucide-react';
import { THEMES } from '../../context/ThemeContext';

interface SettingsSectionProps {
    theme: string;
    setTheme: (theme: any) => void;
    username: string | null;
    logout: () => void;
}

export const SettingsSection = ({ theme, setTheme, username, logout }: SettingsSectionProps) => {
    return (
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
    );
};
