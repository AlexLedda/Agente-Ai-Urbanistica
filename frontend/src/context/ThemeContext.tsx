import React, { createContext, useContext, useState, useEffect } from 'react';

type Theme = 'ocean' | 'forest' | 'sunset' | 'royal';

interface ThemeContextType {
    theme: Theme;
    setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [theme, setThemeState] = useState<Theme>(() => {
        const saved = localStorage.getItem('urbanai-theme');
        return (saved as Theme) || 'ocean';
    });

    const setTheme = (newTheme: Theme) => {
        setThemeState(newTheme);
        localStorage.setItem('urbanai-theme', newTheme);
    };

    useEffect(() => {
        // Remove old theme classes
        document.documentElement.classList.remove('theme-ocean', 'theme-forest', 'theme-sunset', 'theme-royal');
        // Add new theme class
        document.documentElement.classList.add(`theme-${theme}`);
    }, [theme]);

    return (
        <ThemeContext.Provider value={{ theme, setTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) throw new Error('useTheme must be used within a ThemeProvider');
    return context;
};

// Helper for UI labels
export const THEMES = [
    { id: 'ocean', label: 'Ocean Blue', color: 'bg-blue-500' },
    { id: 'forest', label: 'Forest Green', color: 'bg-emerald-500' },
    { id: 'sunset', label: 'Sunset Orange', color: 'bg-orange-500' },
    { id: 'royal', label: 'Royal Purple', color: 'bg-violet-500' },
];
