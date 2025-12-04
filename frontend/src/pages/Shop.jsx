import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import './Shop.css';

export default function Shop() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const raffleId = searchParams.get('raffle');
  const { user, refreshUser, loading: authLoading } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Only load products after auth is complete
    if (!authLoading) {
      loadProducts();
    }
  }, [authLoading]);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await productAPI.getProducts();
      setProducts(data);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProductClick = (productId) => {
    const url = raffleId 
      ? `/product/${productId}?raffle=${raffleId}`
      : `/product/${productId}`;
    navigate(url);
  };

  if (loading) {
    return (
      <div className="shop">
        <div className="loading">Loading products...</div>
      </div>
    );
  }

  return (
    <div className="shop">
      <div className="shop-header">
        <h1>🛒 Shop</h1>
        <p className="subtitle">
          {raffleId ? 'Buy products to get entries for this raffle' : 'Select a raffle to see products'}
        </p>
        {!raffleId && (
          <p style={{ color: 'var(--tg-theme-hint-color, #999)', fontSize: '14px', marginTop: '8px' }}>
            Go to the home page and select a raffle to purchase products
          </p>
        )}
      </div>

      {products.length === 0 ? (
        <Card>
          <div className="empty-state">
            <div className="empty-icon">📦</div>
            <p>No products available</p>
          </div>
        </Card>
      ) : (
        <div className="products-list">
          {products.map((product) => {
            return (
              <Card 
                key={product.id}
                onClick={() => handleProductClick(product.id)}
              >
                <div className="product-card">
                  {product.image && (
                    <div className="product-image">
                      <img src={product.image} alt={product.name} />
                    </div>
                  )}
                  <div className="product-info">
                    <h3>{product.name}</h3>
                    <p className="product-description">{product.description}</p>
                    <div className="product-rewards">
                      <div className="reward-item">
                        <span className="reward-label">Entries:</span>
                        <span className="reward-value">+{product.entries_per_product} entries</span>
                      </div>
                    </div>
                    <div className="product-footer">
                      <div className="product-price">
                        <span className="price-value">${product.price}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}




