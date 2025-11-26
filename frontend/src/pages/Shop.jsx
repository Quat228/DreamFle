import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { productAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import './Shop.css';

export default function Shop() {
  const { user, refreshUser } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(null);

  useEffect(() => {
    loadProducts();
  }, []);

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

  const handlePurchase = async (productId) => {
    if (!user) {
      alert('Please authenticate first');
      return;
    }

    const cost = parseFloat(products.find(p => p.id === productId)?.price_credits || 0);
    if (user.credit_balance < cost) {
      alert('Insufficient credits!');
      return;
    }

    if (!confirm('Purchase this product?')) {
      return;
    }

    try {
      setPurchasing(productId);
      await productAPI.purchaseProduct(productId);
      await refreshUser();
      alert('Purchase successful!');
    } catch (error) {
      console.error('Error purchasing product:', error);
      alert(error.response?.data?.detail || 'Failed to purchase product');
    } finally {
      setPurchasing(null);
    }
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
        <p className="subtitle">Buy tokens and credits</p>
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
            const canAfford = user && parseFloat(user.credit_balance || 0) >= parseFloat(product.price_credits || 0);
            
            return (
              <Card key={product.id}>
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
                        <span className="reward-label">Reward:</span>
                        <span className="reward-value">+{product.reward_tokens} tokens</span>
                      </div>
                    </div>
                    <div className="product-footer">
                      <div className="product-price">
                        <span className="price-value">{product.price_credits}</span>
                        <span className="price-currency">credits</span>
                      </div>
                      <Button
                        variant={canAfford ? 'primary' : 'secondary'}
                        onClick={() => handlePurchase(product.id)}
                        disabled={!canAfford || purchasing === product.id}
                        size="small"
                      >
                        {purchasing === product.id ? 'Purchasing...' : 'Buy'}
                      </Button>
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

