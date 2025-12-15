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
      // Check if this is a CRM endpoint - use CRM token if available
      const isCRMEndpoint = config.url?.startsWith('/crm/');
      const tokenKey = isCRMEndpoint ? 'crm_access' : 'access';
      const token = localStorage.getItem(tokenKey);
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
    
    // Don't retry refresh for auth endpoints
    if (originalRequest.url?.includes('/auth/')) {
      return Promise.reject(error);
    }
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      // Check if this is a CRM endpoint
      const isCRMEndpoint = originalRequest.url?.includes('/crm/');
      const refreshKey = isCRMEndpoint ? 'crm_refresh' : 'refresh';
      const accessKey = isCRMEndpoint ? 'crm_access' : 'access';
      const refresh = localStorage.getItem(refreshKey);
      
      if (refresh) {
        try {
          // Try to refresh token
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh,
          });
          const { access } = response.data;
          localStorage.setItem(accessKey, access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        } catch (err) {
          // If refresh fails (user doesn't exist, token invalid, etc.)
          console.error('Token refresh failed:', err);
          localStorage.removeItem(accessKey);
          localStorage.removeItem(refreshKey);
          
          // If it's a user not found error or invalid token, trigger re-auth
          if (err.response?.status === 500 || 
              err.response?.status === 401 ||
              err.response?.data?.detail?.includes('DoesNotExist') ||
              err.response?.data?.detail?.includes('invalid') ||
              err.response?.data?.detail?.includes('expired')) {
            // Clear everything - the app will re-authenticate on next load
            console.warn('[API] Token refresh failed, user needs to re-authenticate');
          }
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

// Coupon API
export const couponAPI = {
  getMyCoupons: async () => {
    const response = await api.get('/payments/coupons/');
    return response.data;
  },
  getCoupon: async (id) => {
    const response = await api.get(`/payments/coupons/${id}/`);
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
  // enterRaffle removed - entries now come from product purchases
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
  getProduct: async (id) => {
    const response = await api.get(`/products/${id}/`);
    return response.data;
  },
  purchaseProduct: async (id, raffleId) => {
    const response = await api.post(`/products/${id}/purchase/`, {
      raffle_id: raffleId,
    });
    return response.data;
  },
};

// CRM API
export const crmAPI = {
  login: async (username, password) => {
    const response = await api.post('/crm/auth/login/', {
      username,
      password,
    });
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/crm/auth/me/');
    return response.data;
  },
  getRaffles: async () => {
    const response = await api.get('/crm/raffles/');
    return response.data;
  },
  getRaffle: async (id) => {
    const response = await api.get(`/crm/raffles/${id}/`);
    return response.data;
  },
  updateRaffleStartTime: async (id, newStartAt) => {
    const response = await api.post(`/crm/raffles/${id}/update-start-time/`, {
      new_start_at: newStartAt,
    });
    return response.data;
  },
};

export default api;

