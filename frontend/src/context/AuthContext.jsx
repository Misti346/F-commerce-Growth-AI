import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

function readStoredUser() {
  try {
    const raw = localStorage.getItem('fcommerce_user');
    if (!raw) return null;

    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : null;
  } catch (error) {
    localStorage.removeItem('fcommerce_user');
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => readStoredUser());
  const [token, setToken] = useState(() => localStorage.getItem('fcommerce_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const bootstrap = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await api.get('/api/auth/profile');
        const nextUser = response.data.user;
        setUser(nextUser);
        localStorage.setItem('fcommerce_user', JSON.stringify(nextUser));
        localStorage.setItem('seller_id', String(nextUser.user_id));
      } catch (error) {
        setUser(null);
        localStorage.removeItem('fcommerce_token');
        localStorage.removeItem('fcommerce_user');
        localStorage.removeItem('seller_id');
        setToken(null);
      } finally {
        setLoading(false);
      }
    };

    bootstrap();
  }, [token]);

  const login = async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password });
    const accessToken = response.data.access_token;
    const nextUser = response.data.user;

    localStorage.setItem('fcommerce_token', accessToken);
    localStorage.setItem('fcommerce_user', JSON.stringify(nextUser));
    localStorage.setItem('seller_id', String(nextUser.user_id));
    setToken(accessToken);
    setUser(nextUser);

    return response.data;
  };

  const register = async (name, email, password) => {
    const response = await api.post('/api/auth/register', { name, email, password });
    return response.data;
  };

  const forgotPassword = async (email) => {
    const response = await api.post('/api/auth/forgot-password', { email });
    return response.data;
  };

  const resetPassword = async (token, newPassword) => {
    const response = await api.post('/api/auth/reset-password', {
      token,
      new_password: newPassword
    });
    return response.data;
  };

  const logout = async (calledFromClient = true) => {
    try {
      if (calledFromClient && token) {
        await api.post('/api/auth/logout');
      }
    } catch (error) {
      console.warn('Logout request failed:', error);
    } finally {
      localStorage.removeItem('fcommerce_token');
      localStorage.removeItem('fcommerce_user');
      localStorage.removeItem('seller_id');
      setToken(null);
      setUser(null);
    }
  };

  const refreshProfile = async () => {
    if (!token) return null;
    const response = await api.get('/api/auth/profile');
    setUser(response.data.user);
    localStorage.setItem('fcommerce_user', JSON.stringify(response.data.user));
    localStorage.setItem('seller_id', String(response.data.user.user_id));
    return response.data.user;
  };

  const value = useMemo(
    () => ({ user, token, loading, login, register, forgotPassword, resetPassword, logout, refreshProfile }),
    [user, token, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
