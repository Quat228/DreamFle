import React, { useEffect, useState } from 'react';
import { HashRouter, MemoryRouter, BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { CRMAuthProvider, useCRMAuth } from './contexts/CRMAuthContext';
import Layout from './components/Layout';
import CRMLayout from './components/CRMLayout';
import Home from './pages/Home';
import RaffleDetail from './pages/RaffleDetail';
import RaffleLive from './pages/RaffleLive';
import Shop from './pages/Shop';
import ProductDetail from './pages/ProductDetail';
import MyEntries from './pages/MyEntries';
import PreviousRaffles from './pages/PreviousRaffles';
import Profile from './pages/Profile';
import CouponDetail from './pages/CouponDetail';
import CRMLogin from './pages/crm/CRMLogin';
import CRMHome from './pages/crm/CRMHome';
import CRMRafflesList from './pages/crm/CRMRafflesList';
import CRMRaffleDetail from './pages/crm/CRMRaffleDetail';
import ProtectedCRMRoute from './components/ProtectedCRMRoute';
import './App.css';

// Detect if we're in Telegram Mini App
const isTelegramWebApp = () => {
  return window.Telegram?.WebApp || window.location.hash.includes('tgWebAppData');
};

// Router component that syncs with hash when not in Telegram (for main app)
function RouterSync({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isTelegram] = useState(isTelegramWebApp);

  useEffect(() => {
    if (!isTelegram) {
      // Sync MemoryRouter with hash for non-Telegram environments
      const hash = window.location.hash.replace('#', '') || '/';
      if (hash !== location.pathname) {
        navigate(hash);
      }
    }
  }, [isTelegram, navigate, location.pathname]);

  useEffect(() => {
    if (!isTelegram && location.pathname) {
      // Update hash when route changes in non-Telegram
      window.location.hash = location.pathname;
    }
  }, [location.pathname, isTelegram]);

  return <>{children}</>;
}

// Simple router sync for CRM (no hash needed, uses BrowserRouter)
function CRMRouterSync({ children }) {
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/raffle/:id" element={<RaffleDetail />} />
      <Route path="/raffle/:id/live" element={<RaffleLive />} />
      <Route path="/shop" element={<Shop />} />
      <Route path="/product/:id" element={<ProductDetail />} />
      <Route path="/entries" element={<MyEntries />} />
      <Route path="/previous-raffles" element={<PreviousRaffles />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/coupon/:id" element={<CouponDetail />} />
    </Routes>
  );
}

function CRMRoutes() {
  return (
    <Routes>
      <Route 
        path="/login" 
        element={<CRMLogin />} 
      />
      <Route 
        path="/" 
        element={
          <ProtectedCRMRoute>
            <CRMHome />
          </ProtectedCRMRoute>
        } 
      />
      <Route 
        path="/raffles" 
        element={
          <ProtectedCRMRoute>
            <CRMRafflesList />
          </ProtectedCRMRoute>
        } 
      />
      <Route 
        path="/raffles/:id" 
        element={
          <ProtectedCRMRoute>
            <CRMRaffleDetail />
          </ProtectedCRMRoute>
        } 
      />
    </Routes>
  );
}

export default function App() {
  const isTelegram = isTelegramWebApp();
  console.log('[App] Component rendering, isTelegram:', isTelegram);
  console.log('[App] Current location:', window.location.href);
  console.log('[App] Hash:', window.location.hash);
  
  const RouterComponent = isTelegram ? MemoryRouter : HashRouter;
  const initialEntries = isTelegram ? ['/'] : undefined;
  
  // Check if we're on a CRM route
  // For CRM, we check the actual pathname since it's served directly by Django at /crm/
  const currentPath = window.location.pathname;
  const isCRMRoute = currentPath.startsWith('/crm');

  if (isCRMRoute) {
    // Use BrowserRouter for CRM since it's served directly by Django at /crm/
    return (
      <CRMAuthProvider>
        <BrowserRouter basename="/crm">
          <CRMRouterSync>
            <CRMLayout>
              <CRMRoutes />
            </CRMLayout>
          </CRMRouterSync>
        </BrowserRouter>
      </CRMAuthProvider>
    );
  }

  return (
    <AuthProvider>
      <RouterComponent initialEntries={initialEntries}>
        <RouterSync>
          <Layout>
            <AppRoutes />
          </Layout>
        </RouterSync>
      </RouterComponent>
    </AuthProvider>
  );
}
