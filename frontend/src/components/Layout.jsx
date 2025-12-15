import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Layout.css';

export default function Layout({ children }) {
  const location = useLocation();
  const { user, loading } = useAuth();

  const navItems = [
    { path: '/', label: 'Raffles', icon: '🎰' },
    { path: '/shop', label: 'Shop', icon: '🛒' },
    { path: '/entries', label: 'My Entries', icon: '🎫' },
    { path: '/previous-raffles', label: 'Previous', icon: '🏆' },
    { path: '/profile', label: 'Profile', icon: '👤' },
  ];

  // Show loading screen while authenticating
  if (loading) {
    return (
      <div className="layout">
        <div className="layout-content" style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh',
          padding: '20px'
        }}>
          <div className="loading">Authenticating...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="layout">
      <div className="layout-content">{children}</div>
      <nav className="bottom-nav">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </Link>
        ))}
      </nav>
      <footer className="site-footer"></footer>
    </div>
  );
}

