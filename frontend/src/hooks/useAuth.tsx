'use client';

import { User } from '@/lib/api/types';
import { login as apiLogin, logout as apiLogout, getUserProfile } from '@/lib/auth/api';
import { userStorage } from '@/lib/auth/storage';
import { useRouter } from 'next/navigation';
import { createContext, ReactNode, useContext, useEffect, useState } from 'react';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      // First try to get user from localStorage (fast)
      const cachedUser = userStorage.getUser();
      if (cachedUser) {
        setUser(cachedUser);
        setLoading(false);
        return;
      }

      // If not in localStorage, check with API (cookie-based)
      const response = await getUserProfile();
      if (response.data) {
        setUser(response.data);
        userStorage.setUser(response.data);
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    const response = await apiLogin(username, password);

    if (response.error) {
      return { success: false, error: response.error };
    }

    if (response.data) {
      setUser(response.data.user);
      router.push('/dashboard');
      return { success: true };
    }

    return { success: false, error: 'Unexpected error' };
  };

  const logout = async () => {
    await apiLogout();
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
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

