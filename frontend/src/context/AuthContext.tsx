import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

interface AuthContextType {
    token: string | null;
    login: (token: string, username: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
    username: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
    const [username, setUsername] = useState<string | null>(localStorage.getItem('username'));

    useEffect(() => {
        if (token) {
            localStorage.setItem('token', token);
        } else {
            localStorage.removeItem('token');
        }

        if (username) {
            localStorage.setItem('username', username);
        } else {
            localStorage.removeItem('username');
        }
    }, [token, username]);

    const login = (newToken: string, newUsername: string) => {
        setToken(newToken);
        setUsername(newUsername);
    };

    const logout = () => {
        setToken(null);
        setUsername(null);
    };

    return (
        <AuthContext.Provider value={{ token, login, logout, isAuthenticated: !!token, username }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
