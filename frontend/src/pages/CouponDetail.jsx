import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { couponAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import './CouponDetail.css';

export default function CouponDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [coupon, setCoupon] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading) {
      loadCoupon();
    }
  }, [id, authLoading]);

  const loadCoupon = async () => {
    try {
      setLoading(true);
      const data = await couponAPI.getCoupon(id);
      setCoupon(data);
    } catch (error) {
      console.error('Error loading coupon:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="coupon-detail">
        <div className="loading">Loading coupon details...</div>
      </div>
    );
  }

  if (!coupon) {
    return (
      <div className="coupon-detail">
        <Card>
          <div className="error-state">
            <p>Coupon not found</p>
            <Button onClick={() => navigate('/profile')}>Go Back</Button>
          </div>
        </Card>
      </div>
    );
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'referral':
        return '👥';
      case 'lost':
        return '🎲';
      default:
        return '🎫';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'referral':
        return '#4caf50';
      case 'lost':
        return '#ff9800';
      default:
        return '#2196f3';
    }
  };

  return (
    <div className="coupon-detail">
      <div className="coupon-header">
        <div className="coupon-icon-large" style={{ backgroundColor: getTypeColor(coupon.type) }}>
          {getTypeIcon(coupon.type)}
        </div>
        <h1>{coupon.name}</h1>
      </div>

      <Card>
        <h3>Coupon Information</h3>
        <div className="coupon-info-grid">
          <div className="info-item">
            <span className="info-label">Type</span>
            <span className="info-value">{coupon.type_display}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Bonus Entries</span>
            <span className="info-value highlight">+{coupon.entries} entries</span>
          </div>
        </div>
      </Card>

      <Card>
        <h3>How to Use</h3>
        <div className="coupon-usage">
          <p>This coupon automatically applies when you purchase any product!</p>
          <p className="usage-hint">
            When you buy a product, you'll receive the base entries plus {coupon.entries} bonus entries from this coupon.
          </p>
        </div>
      </Card>

      <div className="action-section">
        <Button
          fullWidth
          variant="primary"
          onClick={() => navigate('/shop')}
        >
          Go to Shop
        </Button>
        <Button
          fullWidth
          variant="secondary"
          onClick={() => navigate('/profile')}
        >
          Back to Profile
        </Button>
      </div>
    </div>
  );
}

