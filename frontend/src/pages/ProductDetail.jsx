import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productAPI, raffleAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import './ProductDetail.css';

export default function ProductDetail() {
  const { id } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, refreshUser, loading: authLoading } = useAuth();
  const [product, setProduct] = useState(null);
  const [raffles, setRaffles] = useState([]);
  const [selectedRaffleId, setSelectedRaffleId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);

  useEffect(() => {
    if (!authLoading) {
      loadData();
    }
  }, [id, authLoading]);

  useEffect(() => {
    // Set selected raffle from URL parameter
    const raffleIdFromUrl = searchParams.get('raffle');
    if (raffleIdFromUrl) {
      setSelectedRaffleId(String(raffleIdFromUrl));
    } else {
      setSelectedRaffleId(null);
    }
  }, [searchParams]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [productData, rafflesData] = await Promise.all([
        productAPI.getProduct(id),
        raffleAPI.getRaffles(),
      ]);
      setProduct(productData);
      setRaffles(rafflesData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRaffleSelect = (raffleId) => {
    const raffleIdStr = String(raffleId);
    // Toggle: if clicking the same raffle, unselect it
    if (selectedRaffleId === raffleIdStr) {
      setSelectedRaffleId(null);
      setSearchParams({});
    } else {
      setSelectedRaffleId(raffleIdStr);
      setSearchParams({ raffle: raffleIdStr });
    }
  };

  const handlePurchase = async () => {
    if (!user) {
      alert('Please authenticate first');
      return;
    }

    if (!selectedRaffleId) {
      alert('Please select a raffle first');
      return;
    }

    if (!product) {
      alert('Product not found');
      return;
    }

    const totalEntries = product.entries_per_product + (user.bonus_entries || 0);
    const bonusText = user.bonus_entries > 0 ? ` (${product.entries_per_product} base + ${user.bonus_entries} bonus)` : '';
    if (!confirm(`Purchase ${product.name} and receive ${totalEntries} entries${bonusText}?`)) {
      return;
    }

    try {
      setPurchasing(true);
      const result = await productAPI.purchaseProduct(product.id, selectedRaffleId);
      await refreshUser();
      alert(`Purchase successful! You received ${result.entries_granted} entries!`);
    } catch (error) {
      console.error('Error purchasing product:', error);
      alert(error.response?.data?.detail || 'Failed to purchase product');
    } finally {
      setPurchasing(false);
    }
  };

  if (loading) {
    return (
      <div className="product-detail">
        <div className="loading">Loading product details...</div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="product-detail">
        <Card>
          <div className="error-state">
            <p>Product not found</p>
            <Button onClick={() => navigate('/shop')}>Go Back</Button>
          </div>
        </Card>
      </div>
    );
  }

  // Filter only active raffles
  const activeRaffles = raffles.filter(r => r.is_active && !r.is_finished);

  return (
    <div className="product-detail">
      {/* Raffle Selector */}
      {activeRaffles.length > 0 && (
        <Card>
          <div className="raffle-selector">
            <h3>Select Raffle</h3>
            <p className="selector-hint">Choose which raffle to get entries for</p>
            <div className="raffle-options">
              {activeRaffles.map((raffle) => {
                const raffleIdStr = String(raffle.id);
                const isSelected = selectedRaffleId === raffleIdStr;
                return (
                  <button
                    key={raffle.id}
                    className={`raffle-option ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleRaffleSelect(raffle.id)}
                  >
                    <div className="raffle-option-content">
                      <div className="raffle-option-name">{raffle.name}</div>
                      {raffle.prize && (
                        <div className="raffle-option-prize">Prize: {raffle.prize.name}</div>
                      )}
                    </div>
                    {isSelected && (
                      <div className="raffle-option-check">✓</div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </Card>
      )}

      {/* Product Details */}
      {product.image && (
        <div className="product-hero-image">
          <img src={product.image} alt={product.name} />
        </div>
      )}

      <Card>
        <div className="product-header">
          <h1>{product.name}</h1>
        </div>
        {product.description && (
          <p className="product-description">{product.description}</p>
        )}
      </Card>

      <Card>
        <h3>Product Information</h3>
        <div className="product-info-grid">
          <div className="info-item">
            <span className="info-label">Price</span>
            <span className="info-value">${product.price}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Entries per Product</span>
            <span className="info-value">+{product.entries_per_product} entries</span>
          </div>
          {user && user.bonus_entries > 0 && (
            <div className="info-item">
              <span className="info-label">Bonus Entries</span>
              <span className="info-value">+{user.bonus_entries} entries</span>
            </div>
          )}
        </div>
      </Card>

      {/* Purchase Button */}
      {user && (
        <div className="action-section">
          <Button
            fullWidth
            variant="primary"
            onClick={handlePurchase}
            disabled={!selectedRaffleId || purchasing}
          >
            {purchasing ? 'Purchasing...' : 'Buy Now'}
          </Button>
          {!selectedRaffleId && (
            <p className="purchase-hint">Please select a raffle above to purchase</p>
          )}
        </div>
      )}

      {!user && (
        <div className="action-section">
          <Button fullWidth onClick={() => navigate('/profile')}>
            Authenticate to Purchase
          </Button>
        </div>
      )}
    </div>
  );
}

