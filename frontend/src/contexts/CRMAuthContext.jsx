import React, { createContext, useContext, useState, useEffect } from 'react';
import { crmAPI } from '../services/api';

const CRMAuthContext = createContext();

export const useCRMAuth = () => {
  const context = useContext(CRMAuthContext);
  if (!context) {
    throw new Error('useCRMAuth must be used within CRMAuthProvider');
  }
  return context;
};

export const CRMAuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true); // Start with true to check auth on mount

  // Check for existing token on mount and verify it
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('crm_access');
      if (token) {
        try {
          // Verify token is still valid by calling /me endpoint
          const userData = await crmAPI.getMe();
          setUser(userData);
          setAuthenticated(true);
        } catch (error) {
          // Token is invalid, clear it
          console.error('[CRM Auth] Token verification failed:', error);
          localStorage.removeItem('crm_access');
          localStorage.removeItem('crm_refresh');
          setUser(null);
          setAuthenticated(false);
        }
      } else {
        setAuthenticated(false);
      }
      setLoading(false);
    };
    
    checkAuth();
  }, []);

  const login = async (username, password) => {
    try {
      setLoading(true);
      const authData = await crmAPI.login(username, password);
      
      if (authData.access) {
        localStorage.setItem('crm_access', authData.access);
        localStorage.setItem('crm_refresh', authData.refresh);
        
        if (authData.user) {
          setUser(authData.user);
          setAuthenticated(true);
          return { success: true };
        }
      }
      return { success: false, error: 'Authentication failed' };
    } catch (error) {
      console.error('[CRM Auth] Login error:', error);
      const errorMessage = error.response?.data?.detail || 'Login failed';
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('crm_access');
    localStorage.removeItem('crm_refresh');
    setUser(null);
    setAuthenticated(false);
  };

  return (
    <CRMAuthContext.Provider
      value={{
        user,
        authenticated,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </CRMAuthContext.Provider>
  );
};
