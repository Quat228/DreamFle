import axios from 'axios';

const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    // Don't override Authorization header if it's already set (e.g., for Telegram auth)
    if (!config.headers.Authorization) {
      const token = localStorage.getItem('access');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refresh = localStorage.getItem('refresh');
      if (refresh) {
        try {
          // Try to refresh token - adjust endpoint if different
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh,
          });
          const { access } = response.data;
          localStorage.setItem('access', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        } catch (err) {
          // If refresh fails, clear tokens and reload
          localStorage.removeItem('access');
          localStorage.removeItem('refresh');
          // Don't reload in mini app, just let user re-authenticate
          console.error('Token refresh failed:', err);
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  telegramAuth: async (initDataRaw) => {
    console.log('[Auth API] Sending telegram auth request');
    console.log('[Auth API] initDataRaw length:', initDataRaw ? initDataRaw.length : 'undefined');
    console.log('[Auth API] initDataRaw preview:', initDataRaw ? initDataRaw.substring(0, 100) + '...' : 'undefined');
    
    const authHeader = `tma ${initDataRaw}`;
    console.log('[Auth API] Authorization header preview:', authHeader.substring(0, 100) + '...');
    
    const response = await api.post('/auth/telegram/', {}, {
      headers: {
        Authorization: authHeader,
      },
    });
    return response.data;
  },
};

// User API
export const userAPI = {
  getMe: async () => {
    const response = await api.get('/users/me/');
    return response.data;
  },
  getReferrals: async () => {
    const response = await api.get('/users/referrals/');
    return response.data;
  },
};

// Raffle API
export const raffleAPI = {
  getRaffles: async () => {
    const response = await api.get('/lottery/raffles/');
    return response.data;
  },
  getRaffle: async (id) => {
    const response = await api.get(`/lottery/raffles/${id}/`);
    return response.data;
  },
  enterRaffle: async (id) => {
    const response = await api.post(`/lottery/raffles/${id}/enter/`);
    return response.data;
  },
  getMyEntries: async () => {
    const response = await api.get('/lottery/entries/');
    return response.data;
  },
  getTransparency: async (id) => {
    const response = await api.get(`/lottery/raffles/${id}/transparency/`);
    return response.data;
  },
};

// Product API
export const productAPI = {
  getProducts: async () => {
    const response = await api.get('/products/');
    return response.data;
  },
  purchaseProduct: async (id) => {
    const response = await api.post(`/products/${id}/purchase/`);
    return response.data;
  },
};

export default api;

