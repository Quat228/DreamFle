import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Layout.css';

export default function Layout({ children }) {
  const location = useLocation();
  const { user } = useAuth();

  const navItems = [
    { path: '/', label: 'Raffles', icon: '🎰' },
    { path: '/shop', label: 'Shop', icon: '🛒' },
    { path: '/entries', label: 'My Entries', icon: '🎫' },
    { path: '/profile', label: 'Profile', icon: '👤' },
  ];

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
      {user && (
        <div className="balance-bar">
          <div className="balance-item">
            <span className="balance-label">Tokens:</span>
            <span className="balance-value">{parseFloat(user.token_balance || 0).toFixed(2)}</span>
          </div>
          <div className="balance-item">
            <span className="balance-label">Credits:</span>
            <span className="balance-value">{parseFloat(user.credit_balance || 0).toFixed(2)}</span>
          </div>
        </div>
      )}
      <footer className="site-footer"></footer>
    </div>
  );
}

