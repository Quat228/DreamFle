import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Card from '../components/Card';
import Button from '../components/Button';
import './Welcome.css';

export default function Welcome() {
  const navigate = useNavigate();
  const { user, authenticated } = useAuth();
  
  console.log('[Welcome] Component rendering, authenticated:', authenticated, 'user:', user);

  console.log('[Welcome] Rendering JSX');
  
  return (
    <div className="welcome" style={{ minHeight: '400px', padding: '20px' }}>
      <div className="welcome-header">
        <h1 style={{ fontSize: '36px', margin: '0 0 12px 0' }}>🎰 NFT Lottery</h1>
        <p className="welcome-subtitle">Welcome to the future of NFT raffles!</p>
      </div>

      <Card>
        <div className="welcome-content">
          <div className="welcome-icon">🎲</div>
          <h2>How it works</h2>
          <div className="welcome-description">
            <p>
              Participate in exciting NFT raffles and win amazing prizes! 
              Use tokens to enter raffles and stand a chance to win rare NFTs.
            </p>
            <p>
              Browse active raffles, check out the shop for token packs, 
              and track your entries all in one place.
            </p>
          </div>
          
          {authenticated ? (
            <div className="welcome-actions">
              <Button 
                onClick={() => navigate('/raffles')}
                className="welcome-button primary"
              >
                View Raffles 🎰
              </Button>
              <Button 
                onClick={() => navigate('/shop')}
                className="welcome-button secondary"
              >
                Visit Shop 🛒
              </Button>
            </div>
          ) : (
            <div className="welcome-auth">
              <p className="welcome-auth-text">
                Please authorize through Telegram to start playing!
              </p>
            </div>
          )}
        </div>
      </Card>

      <div className="welcome-features">
        <div className="feature-item">
          <span className="feature-icon">🎫</span>
          <span className="feature-text">Enter Raffles</span>
        </div>
        <div className="feature-item">
          <span className="feature-icon">🏆</span>
          <span className="feature-text">Win Prizes</span>
        </div>
        <div className="feature-item">
          <span className="feature-icon">💎</span>
          <span className="feature-text">Collect NFTs</span>
        </div>
      </div>
    </div>
  );
}

