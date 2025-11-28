import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import './Profile.css';

export default function Profile() {
  const { user, loading: authLoading, refreshUser } = useAuth();
  const [referrals, setReferrals] = useState([]);
  const [loadingReferrals, setLoadingReferrals] = useState(false);

  useEffect(() => {
    if (user) {
      loadReferrals();
    }
  }, [user]);

  const loadReferrals = async () => {
    try {
      setLoadingReferrals(true);
      const data = await userAPI.getReferrals();
      setReferrals(data);
    } catch (error) {
      console.error('Error loading referrals:', error);
    } finally {
      setLoadingReferrals(false);
    }
  };

  const copyReferralCode = () => {
    if (user?.referral_code) {
      const url = `https://t.me/YOUR_BOT_USERNAME?start=${user.referral_code}`;
      navigator.clipboard.writeText(url);
      alert('Referral link copied to clipboard!');
    }
  };

  if (authLoading) {
    return (
      <div className="profile">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="profile">
        <Card>
          <div className="empty-state">
            <div className="empty-icon">🔐</div>
            <p>Please authenticate to view your profile</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="profile">
      <div className="profile-header">
        <h1>👤 Profile</h1>
      </div>

      <Card>
        <div className="profile-info">
          <div className="profile-avatar">
            {user.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="profile-details">
            <h2>{user.username || `User ${user.id}`}</h2>
            <p className="profile-id">ID: {user.telegram_id || 'N/A'}</p>
          </div>
        </div>
      </Card>

      <Card>
        <h3>Balances</h3>
        <div className="balances-grid">
          <div className="balance-card">
            <div className="balance-icon">🪙</div>
            <div className="balance-details">
              <span className="balance-label">Tokens</span>
              <span className="balance-amount">
                {parseFloat(user.token_balance || 0).toFixed(2)}
              </span>
            </div>
          </div>
          <div className="balance-card">
            <div className="balance-icon">💳</div>
            <div className="balance-details">
              <span className="balance-label">Credits</span>
              <span className="balance-amount">
                {parseFloat(user.credit_balance || 0).toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <h3>Referral Program</h3>
        <div className="referral-section">
          <div className="referral-code">
            <span className="referral-label">Your Referral Code:</span>
            <div className="referral-code-display">
              <code>{user.referral_code}</code>
              <Button size="small" onClick={copyReferralCode}>
                Copy Link
              </Button>
            </div>
          </div>
          <div className="referral-stats">
            <div className="stat-item">
              <span className="stat-value">{referrals.length}</span>
              <span className="stat-label">Referrals</span>
            </div>
          </div>
        </div>
      </Card>

      {referrals.length > 0 && (
        <Card>
          <h3>Your Referrals</h3>
          <div className="referrals-list">
            {referrals.map((referral) => (
              <div key={referral.id} className="referral-item">
                <div className="referral-avatar">
                  {referral.username?.[0]?.toUpperCase() || 'U'}
                </div>
                <div className="referral-info">
                  <span className="referral-name">{referral.username || `User ${referral.id}`}</span>
                  <span className="referral-date">
                    Joined {new Date(referral.date_joined).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <div className="profile-actions">
        <Button
          variant="secondary"
          fullWidth
          onClick={refreshUser}
        >
          Refresh Profile
        </Button>
      </div>
    </div>
  );
}



