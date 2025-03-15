import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginRequest } from '../models/types';
import { apiService, setAuthToken } from '../services/apiService';

// Интерфейс контекста аутентификации
interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
}

// Создание контекста с дефолтными значениями
const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  user: null,
  loading: false,
  error: null,
  login: async () => {},
  logout: () => {},
});

// Хук для использования контекста
export const useAuth = () => useContext(AuthContext);

// Провайдер контекста
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Проверка авторизации при загрузке
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setAuthToken(token);
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  // Получение информации о пользователе
  const fetchUser = async () => {
    try {
      setLoading(true);
      const user = await apiService.getCurrentUser();
      setUser(user);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Ошибка при загрузке пользователя:', error);
      setError('Ошибка авторизации');
      setAuthToken(null);
    } finally {
      setLoading(false);
    }
  };

  // Функция входа
  const login = async (credentials: LoginRequest) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.login(credentials);
      
      setAuthToken(response.access_token);
      await fetchUser();
    } catch (error) {
      console.error('Ошибка входа:', error);
      setError('Неверное имя пользователя или пароль');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Функция выхода
  const logout = () => {
    setAuthToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        loading,
        error,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}; 