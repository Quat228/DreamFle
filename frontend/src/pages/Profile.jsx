import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { userAPI, couponAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import './Profile.css';

export default function Profile() {
  const navigate = useNavigate();
  const { user, loading: authLoading, refreshUser } = useAuth();
  const [referrals, setReferrals] = useState([]);
  const [loadingReferrals, setLoadingReferrals] = useState(false);
  const [coupons, setCoupons] = useState([]);
  const [loadingCoupons, setLoadingCoupons] = useState(false);

  useEffect(() => {
    if (user) {
      loadReferrals();
      loadCoupons();
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

  const loadCoupons = async () => {
    try {
      setLoadingCoupons(true);
      const data = await couponAPI.getMyCoupons();
      setCoupons(data);
    } catch (error) {
      console.error('Error loading coupons:', error);
    } finally {
      setLoadingCoupons(false);
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

      <Card>
        <h3>My Coupons</h3>
        {loadingCoupons ? (
          <div className="loading">Loading coupons...</div>
        ) : coupons.length === 0 ? (
          <div className="empty-state">
            <p>You don't have any coupons yet</p>
            <p className="empty-hint">Earn coupons by participating in raffles!</p>
          </div>
        ) : (
          <div className="coupons-list">
            {coupons.map((userCoupon) => (
              <div
                key={userCoupon.id}
                className="coupon-item"
                onClick={() => navigate(`/coupon/${userCoupon.coupon.id}`)}
                style={{ cursor: 'pointer' }}
              >
                <div className="coupon-icon">🎫</div>
                <div className="coupon-info">
                  <span className="coupon-name">{userCoupon.coupon.name}</span>
                  <span className="coupon-details">
                    +{userCoupon.coupon.entries} bonus entries • {userCoupon.coupon.type_display}
                  </span>
                  <span className="coupon-date">
                    Received {new Date(userCoupon.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="coupon-arrow">→</div>
              </div>
            ))}
          </div>
        )}
      </Card>

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




