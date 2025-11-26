import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { raffleAPI } from '../services/api';
import Card from '../components/Card';
import Button from '../components/Button';
import './Home.css';

export default function Home() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [raffles, setRaffles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRaffles();
  }, []);

  const loadRaffles = async () => {
    try {
      setLoading(true);
      const data = await raffleAPI.getRaffles();
      setRaffles(data);
    } catch (error) {
      console.error('Error loading raffles:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRarityColor = (rarity) => {
    const colors = {
      common: '#9e9e9e',
      uncommon: '#4caf50',
      rare: '#2196f3',
      epic: '#9c27b0',
      legendary: '#ff9800',
    };
    return colors[rarity] || colors.common;
  };

  // Always render header immediately - don't wait for anything
  return (
    <div className="home" style={{ minHeight: '200px' }}>
      <div className="home-header" style={{ padding: '20px 0' }}>
        <h1 style={{ margin: '0 0 8px 0', fontSize: '32px' }}>🎰 NFT Lottery</h1>
        <p className="subtitle" style={{ margin: 0 }}>Win amazing prizes!</p>
      </div>

      {loading ? (
        <Card>
          <div className="loading">Loading raffles...</div>
        </Card>
      ) : raffles.length === 0 ? (
          <Card>
            <div className="empty-state">
              <div className="empty-icon">🎲</div>
              <p>No active raffles at the moment</p>
              <p className="empty-hint">Check back later for new opportunities!</p>
            </div>
          </Card>
        ) : (
          <div className="raffles-list">
            {raffles.map((raffle) => (
              <Card
                key={raffle.id}
                onClick={() => navigate(`/raffle/${raffle.id}`)}
              >
                <div className="raffle-card">
                  {raffle.prize?.image && (
                    <div className="raffle-image">
                      <img src={raffle.prize.image} alt={raffle.prize.name} />
                      {raffle.prize.rarity && (
                        <span
                          className="rarity-badge"
                          style={{ backgroundColor: getRarityColor(raffle.prize.rarity) }}
                        >
                          {raffle.prize.rarity}
                        </span>
                      )}
                    </div>
                  )}
                  <div className="raffle-info">
                    <h3>{raffle.name}</h3>
                    <p className="raffle-description">{raffle.description}</p>
                    <div className="raffle-prize">
                      <strong>Prize:</strong> {raffle.prize?.name}
                    </div>
                    <div className="raffle-meta">
                      <div className="meta-item">
                        <span className="meta-label">Cost:</span>
                        <span className="meta-value">{raffle.cost_tokens} tokens</span>
                      </div>
                      {raffle.min_participants_to_unlock && (
                        <div className="meta-item">
                          <span className="meta-label">Min participants:</span>
                          <span className="meta-value">{raffle.min_participants_to_unlock}</span>
                        </div>
                      )}
                    </div>
                    {raffle.entries_count !== undefined && (
                      <div className="raffle-participants">
                        {raffle.entries_count} participant{raffle.entries_count !== 1 ? 's' : ''}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
    </div>
  );
}

