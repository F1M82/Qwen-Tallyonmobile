import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

interface User {
  id: string;
  email: string;
  full_name: string;
  is_ca: boolean;
  firm_name?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (data: Partial<User>) => void;
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  is_ca: boolean;
  firm_name?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AUTH_TOKEN_KEY = '@taxmind:auth_token';
const USER_DATA_KEY = '@taxmind:user_data';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  async function loadStoredAuth() {
    try {
      const [token, userData] = await AsyncStorage.multiGet([
        AUTH_TOKEN_KEY,
        USER_DATA_KEY,
      ]);

      if (token[1] && userData[1]) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token[1]}`;
        setUser(JSON.parse(userData[1]));
      }
    } catch (error) {
      console.error('Error loading auth:', error);
    } finally {
      setIsLoading(false);
    }
  }

  async function login(email: string, password: string) {
    try {
      const response = await api.post('/auth/login', {
        username: email,
        password,
      });

      const { access_token } = response.data;

      await AsyncStorage.multiSet([
        [AUTH_TOKEN_KEY, access_token],
        [USER_DATA_KEY, JSON.stringify(response.data.user)],
      ]);

      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(response.data.user);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  async function register(data: RegisterData) {
    try {
      const response = await api.post('/auth/register', data);
      
      // Auto-login after registration
      await login(data.email, data.password);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  async function logout() {
    try {
      await AsyncStorage.multiRemove([AUTH_TOKEN_KEY, USER_DATA_KEY]);
      delete api.defaults.headers.common['Authorization'];
      setUser(null);
    } catch (error) {
      console.error('Error logging out:', error);
    }
  }

  function updateUser(data: Partial<User>) {
    if (user) {
      const updatedUser = { ...user, ...data };
      setUser(updatedUser);
      AsyncStorage.setItem(USER_DATA_KEY, JSON.stringify(updatedUser));
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        updateUser,
      }}
    >
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
