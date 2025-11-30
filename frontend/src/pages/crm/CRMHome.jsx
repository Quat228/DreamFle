import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCRMAuth } from '../../contexts/CRMAuthContext';
import Button from '../../components/Button';
import './CRMHome.css';

export default function CRMHome() {
  const navigate = useNavigate();
  const { user, authenticated, logout } = useCRMAuth();

  useEffect(() => {
    if (!authenticated) {
      navigate('/login');
    }
  }, [authenticated, navigate]);

  if (!authenticated) {
    return null;
  }

  return (
    <div className="crm-home">
      <div className="crm-header">
        <h1>🎛️ CRM Portal</h1>
        <div className="crm-user-info">
          <span>Welcome, <strong>{user?.username}</strong></span>
          <Button onClick={logout} variant="secondary" style={{ marginLeft: '10px' }}>
            Logout
          </Button>
        </div>
      </div>

      <div className="crm-content">
        <h2>Management Tools</h2>
        <div className="crm-buttons">
          <div className="crm-button-card" onClick={() => navigate('/raffles')}>
            <div className="crm-button-icon">🎰</div>
            <h3>Raffles</h3>
            <p>Manage raffles, update start times, and view details</p>
          </div>
          {/* Add more buttons here in the future */}
        </div>
      </div>
    </div>
  );
}
