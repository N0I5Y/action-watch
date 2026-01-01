import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
    id: number;
    login: string;
    avatar_url: string;
}

interface Installation {
    id: number;
    account: {
        login: string;
        avatar_url: string;
    };
}

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    installations: Installation[];
    selectedInstallationId: number | null;
    setSelectedInstallationId: (id: number) => void;
    login: () => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [installations, setInstallations] = useState<Installation[]>([]);
    const [selectedInstallationId, setSelectedInstallationId] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check for existing session
        async function checkAuth() {
            try {
                const res = await fetch(`${API_BASE}/auth/me`, {
                    credentials: 'include'
                });
                if (res.ok) {
                    const data = await res.json();
                    setUser(data.user);
                    setInstallations(data.installations || []);
                    if (data.installations?.length > 0) {
                        setSelectedInstallationId(data.installations[0].id);
                    }
                }
            } catch (err) {
                console.error("Auth check failed", err);
            } finally {
                setIsLoading(false);
            }
        }
        checkAuth();
    }, []);

    const login = () => {
        window.location.href = `${API_BASE}/auth/login`;
    };

    const logout = async () => {
        await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        setUser(null);
        setInstallations([]);
    };

    return (
        <AuthContext.Provider value={{
            user,
            isLoading,
            installations,
            selectedInstallationId,
            setSelectedInstallationId,
            login,
            logout
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
