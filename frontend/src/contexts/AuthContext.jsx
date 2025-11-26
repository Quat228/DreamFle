import React, { createContext, useContext, useState, useEffect } from 'react';
import { retrieveLaunchParams } from '@tma.js/sdk';
import { authAPI, userAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      console.log('[Auth] Initializing authentication...');
      let initDataRaw;
      try {
        const params = retrieveLaunchParams();
        initDataRaw = params?.initDataRaw;
      } catch (error) {
        console.warn('[Auth] Error retrieving launch params:', error);
        setLoading(false);
        return;
      }
      
      if (!initDataRaw) {
        console.warn('[Auth] No initDataRaw found. App may not be running in Telegram Mini App.');
        setLoading(false);
        return;
      }

      console.log('[Auth] Found initDataRaw, attempting Telegram authentication...');
      console.log('[Auth] initDataRaw value:', initDataRaw);
      console.log('[Auth] initDataRaw type:', typeof initDataRaw);
      console.log('[Auth] initDataRaw length:', initDataRaw ? initDataRaw.length : 'undefined');
      // Try to authenticate
      const authData = await authAPI.telegramAuth(initDataRaw);
      
      if (authData.access) {
        console.log('[Auth] Authentication successful, storing tokens...');
        localStorage.setItem('access', authData.access);
        localStorage.setItem('refresh', authData.refresh);
        
        // Fetch user data
        console.log('[Auth] Fetching user data...');
        const userData = await userAPI.getMe();
        setUser(userData);
        setAuthenticated(true);
        console.log('[Auth] User authenticated:', userData.username);
      } else {
        console.error('[Auth] Authentication failed: No access token in response');
      }
    } catch (error) {
      console.error('[Auth] Authentication error:', error);
      if (error.response) {
        console.error('[Auth] Error response:', error.response.status, error.response.data);
      } else if (error.request) {
        console.error('[Auth] No response received:', error.request);
      } else {
        console.error('[Auth] Error setting up request:', error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const refreshUser = async () => {
    try {
      console.log('[Auth] Refreshing user data...');
      const userData = await userAPI.getMe();
      setUser(userData);
      console.log('[Auth] User data refreshed:', userData.username);
    } catch (error) {
      console.error('[Auth] Error refreshing user:', error);
      if (error.response) {
        console.error('[Auth] Error response:', error.response.status, error.response.data);
      }
    }
  };

  const logout = () => {
    console.log('[Auth] Logging out...');
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    setUser(null);
    setAuthenticated(false);
    console.log('[Auth] Logged out successfully');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        authenticated,
        refreshUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

