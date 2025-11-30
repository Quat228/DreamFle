import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useCRMAuth } from '../../contexts/CRMAuthContext';
import Button from '../../components/Button';
import './CRMLogin.css';

export default function CRMLogin() {
  const navigate = useNavigate();
  const location = useLocation();
  const { authenticated, loading, login } = useCRMAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (authenticated) {
      // Redirect to the page they were trying to access, or home
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [authenticated, navigate, location]);

  // If already authenticated, redirect immediately
  if (authenticated) {
    const from = location.state?.from?.pathname || '/';
    navigate(from, { replace: true });
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    const result = await login(username, password);
    
    if (result.success) {
      // Redirect to the page they were trying to access, or home
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    } else {
      setError(result.error || 'Login failed');
    }
    
    setSubmitting(false);
  };

  if (loading) {
    return (
      <div className="crm-login">
        <div className="crm-login-container">
          <h1>CRM Portal</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="crm-login">
      <div className="crm-login-container">
        <h1>🔐 CRM Portal</h1>
        <p className="subtitle">Admin Login</p>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={submitting}
              autoComplete="username"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={submitting}
              autoComplete="current-password"
            />
          </div>
          
          {error && (
            <div className="error-message">{error}</div>
          )}
          
          <Button
            type="submit"
            fullWidth
            disabled={submitting || !username || !password}
          >
            {submitting ? 'Logging in...' : 'Login'}
          </Button>
        </form>
      </div>
    </div>
  );
}
