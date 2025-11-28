import React, { useEffect, useState } from 'react';
import { HashRouter, MemoryRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import RaffleDetail from './pages/RaffleDetail';
import Shop from './pages/Shop';
import MyEntries from './pages/MyEntries';
import Profile from './pages/Profile';
import './App.css';

// Detect if we're in Telegram Mini App
const isTelegramWebApp = () => {
  return window.Telegram?.WebApp || window.location.hash.includes('tgWebAppData');
};

// Router component that syncs with hash when not in Telegram
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

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/raffle/:id" element={<RaffleDetail />} />
      <Route path="/shop" element={<Shop />} />
      <Route path="/entries" element={<MyEntries />} />
      <Route path="/profile" element={<Profile />} />
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
